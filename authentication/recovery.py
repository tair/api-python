# PWL-1036: helpers for the unauthenticated account-recovery endpoints
# (/credentials/resetPwd/ and /credentials/getUsernames/).

import hashlib
from datetime import timedelta

from django.db import IntegrityError, OperationalError, transaction
from django.utils import timezone

from authentication.models import AccountRecoveryAttempt, AccountRecoveryLock
from common.common import getRemoteIpAddress

import logging
logger = logging.getLogger('phoenix.api.authentication')

RATE_LIMIT_WINDOW = timedelta(hours=1)

# (action, maximum accepted requests per RATE_LIMIT_WINDOW).
# A reset rotates the password, so a username gets very few per hour; the IP
# limit is looser because many users can share an institution's address.
RESET_PER_USERNAME = ('reset-user', 3)
RESET_PER_IP = ('reset-ip', 20)
USERNAMES_PER_EMAIL = ('names-email', 3)
USERNAMES_PER_IP = ('names-ip', 20)

# Rows older than this are deleted as new ones are written.
RETENTION = timedelta(days=1)

MAX_TRIES = 5
# MySQL deadlock (1213) and lock wait timeout (1205): safe to retry.
RETRYABLE_MYSQL_ERRORS = (1213, 1205)


def _hashKey(value):
    if isinstance(value, unicode):
        value = value.encode('utf-8')
    return hashlib.sha1(value).hexdigest()


def clientIp(request):
    return getRemoteIpAddress(request) or 'unknown'


def _ensureLockRows(keys, now):
    """Create the lock row for each key if it is missing. Runs before the
    locking transaction, so a concurrent insert of the same row only raises
    IntegrityError here, which means the row now exists."""
    for action, keyHash in keys:
        if AccountRecoveryLock.objects.filter(action=action, keyHash=keyHash).exists():
            continue
        try:
            with transaction.atomic():
                AccountRecoveryLock.objects.create(action=action, keyHash=keyHash, lastUsed=now)
        except IntegrityError:
            pass


def reserve(limits):
    """Count one request against each of the given limits, atomically.

    limits: list of ((action, maxCount), key). Returns True and records the
    request if every limit has room; returns False and records nothing if any
    limit is used up.

    Checking the counts and recording the attempt must be one step: otherwise
    two requests can both read count == max - 1 and both pass. So the request
    locks one row per key (in a fixed order, to avoid deadlocks), then counts
    and records while holding the locks. Requests sharing a key wait for each
    other; requests with different keys do not.
    """
    now = timezone.now()
    maxCounts = {}
    for (action, maxCount), key in limits:
        k = (action, _hashKey(key))
        maxCounts[k] = min(maxCount, maxCounts.get(k, maxCount))
    keys = sorted(maxCounts)

    reserved = None
    # Retry when a lock row was purged between creating and locking it, or
    # when MySQL picks this transaction as a deadlock or lock-wait victim
    # (seen when many requests create the same lock row at once).
    for _attempt in range(MAX_TRIES):
        try:
            reserved = _reserveOnce(keys, maxCounts, now)
        except OperationalError as e:
            if not e.args or e.args[0] not in RETRYABLE_MYSQL_ERRORS:
                raise
            logger.warning("Account recovery reserve retrying after MySQL error %s" % e.args[0])
            reserved = None
        if reserved is not None:
            break

    if reserved is None:
        # Could not lock the rows; refuse rather than skip the limit.
        return False
    if reserved:
        try:
            _purge(now)
        except OperationalError:
            # Cleanup only; the next request will try again.
            logger.exception("Account recovery purge failed")
    return reserved


def _reserveOnce(keys, maxCounts, now):
    """One locking pass. Returns True/False, or None if a lock row was missing."""
    since = now - RATE_LIMIT_WINDOW
    _ensureLockRows(keys, now)
    with transaction.atomic():
        locked = [
            AccountRecoveryLock.objects.select_for_update()
                .filter(action=action, keyHash=keyHash).first()
            for action, keyHash in keys
        ]
        if None in locked:
            return None
        for action, keyHash in keys:
            count = AccountRecoveryAttempt.objects.filter(
                action=action, keyHash=keyHash, createdAt__gte=since).count()
            if count >= maxCounts[(action, keyHash)]:
                return False
        AccountRecoveryAttempt.objects.bulk_create([
            AccountRecoveryAttempt(action=action, keyHash=keyHash, createdAt=now)
            for action, keyHash in keys
        ])
        AccountRecoveryLock.objects.filter(pk__in=[lock.pk for lock in locked]).update(lastUsed=now)
        return True


def _purge(now):
    cutoff = now - RETENTION
    AccountRecoveryAttempt.objects.filter(createdAt__lt=cutoff).delete()
    AccountRecoveryLock.objects.filter(lastUsed__lt=cutoff).delete()


def maskEmail(email):
    """Mask the local part the same way the partner login pages do, keeping the
    first and last characters: abcd@x.org -> a**d@x.org, ab@x.org -> a*@x.org,
    a@x.org -> *@x.org. Masking an already masked address returns it unchanged,
    so pages that mask the value again still show the same thing."""
    if not email or '@' not in email:
        return ''
    local, domain = email.split('@', 1)
    if len(local) == 1:
        return '*@' + domain
    if len(local) == 2:
        return local[0] + '*@' + domain
    return local[0] + '*' * (len(local) - 2) + local[-1] + '@' + domain
