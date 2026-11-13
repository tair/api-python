# PWL-1036: helpers for the unauthenticated account-recovery endpoints
# (/credentials/resetPwd/ and /credentials/getUsernames/).

import Queue
import hashlib
import ipaddress
import threading
from datetime import timedelta

from django.conf import settings
from django.core.mail import get_connection
from django.db import IntegrityError, OperationalError, connection, transaction
from django.utils import timezone

from authentication.models import AccountRecoveryAttempt, AccountRecoveryLock

import logging
logger = logging.getLogger('phoenix.api.authentication')

# A rolling 24-hour window.
RATE_LIMIT_WINDOW = timedelta(days=1)

# (action, maximum accepted requests per RATE_LIMIT_WINDOW). A legitimate user
# needs one or two of these a day; anything more is someone else's doing.
RESET_PER_USERNAME = ('reset-user', 3)
RESET_PER_IP = ('reset-ip', 5)
USERNAMES_PER_EMAIL = ('names-email', 3)
USERNAMES_PER_IP = ('names-ip', 5)

# Attempt rows older than this are deleted as new ones are written. Must be
# longer than RATE_LIMIT_WINDOW.
RETENTION = RATE_LIMIT_WINDOW + timedelta(days=1)

# Requests are serialized on a fixed pool of lock rows: each limit key maps to
# one of LOCK_STRIPES rows. The pool never grows, so requests that are turned
# away (or that use a new username or email every time) add no rows.
LOCK_STRIPES = 64

MAX_TRIES = 5
# MySQL deadlock (1213) and lock wait timeout (1205): safe to retry.
RETRYABLE_MYSQL_ERRORS = (1213, 1205)

# Addresses our own proxies (the load balancer) connect from. Override with
# settings.RECOVERY_TRUSTED_PROXIES, a list of CIDRs.
DEFAULT_TRUSTED_PROXIES = (
    u'10.0.0.0/8', u'172.16.0.0/12', u'192.168.0.0/16', u'127.0.0.0/8',
    u'::1/128', u'fc00::/7',
)

# How many of our proxies append to X-Forwarded-For in front of the API: 1 for
# a load balancer alone, 2 for a CDN in front of it. Override with
# settings.RECOVERY_PROXY_HOPS. At most this many hops are skipped, so a client
# that is itself on a private network cannot be skipped too.
DEFAULT_PROXY_HOPS = 1


def _hashKey(value):
    if isinstance(value, unicode):
        value = value.encode('utf-8')
    return hashlib.sha1(value).hexdigest()


def _parseIp(value):
    try:
        return ipaddress.ip_address(unicode(value.strip()))
    except (ValueError, UnicodeDecodeError, AttributeError):
        return None


def _trustedProxies():
    cidrs = getattr(settings, 'RECOVERY_TRUSTED_PROXIES', DEFAULT_TRUSTED_PROXIES)
    return [ipaddress.ip_network(unicode(c), strict=False) for c in cidrs]


def clientIp(request):
    """The client address to rate limit on.

    The leftmost X-Forwarded-For entry is whatever the client sent, so it
    cannot be used: a caller could change it on every request. Instead walk
    the chain from the connection peer leftwards, skipping our own proxies,
    and use the first address that is not one of them. A client can only add
    entries to the left of what our proxies append, so it cannot choose this
    address.

    A hop is skipped only if it is in a trusted range AND fewer than
    RECOVERY_PROXY_HOPS hops have been skipped. Without the cap, a client on a
    private address would itself look like a proxy and be skipped, and the
    walk would reach an entry that client wrote.
    """
    hops = [h for h in request.META.get('HTTP_X_FORWARDED_FOR', '').split(',') if h.strip()]
    hops.append(request.META.get('REMOTE_ADDR', ''))
    trusted = _trustedProxies()
    maxSkips = getattr(settings, 'RECOVERY_PROXY_HOPS', DEFAULT_PROXY_HOPS)
    candidate = None
    skipped = 0
    for hop in reversed(hops):
        ip = _parseIp(hop)
        if ip is None:
            # Unparseable entry: we cannot trust anything left of it.
            break
        candidate = ip
        if skipped >= maxSkips or not any(ip in net for net in trusted):
            break
        skipped += 1
    return str(candidate) if candidate is not None else 'unknown'


# Background work (the username email) runs on a small fixed pool of worker
# threads per process, fed by a bounded queue, so a slow or stalled mail
# server cannot pile up threads and database connections.
BACKGROUND_WORKERS = 2
BACKGROUND_QUEUE_SIZE = 50

# SMTP timeout in seconds when settings.EMAIL_TIMEOUT is not set. Without one,
# Django waits on a stalled mail server forever.
DEFAULT_EMAIL_TIMEOUT = 30

_backgroundQueue = Queue.Queue(maxsize=BACKGROUND_QUEUE_SIZE)
_workersLock = threading.Lock()
_workers = []


def mailConnection():
    """An email connection that gives up on a stalled mail server."""
    timeout = getattr(settings, 'EMAIL_TIMEOUT', None) or DEFAULT_EMAIL_TIMEOUT
    return get_connection(timeout=timeout)


def _worker():
    while True:
        func, args = _backgroundQueue.get()
        try:
            func(*args)
        except Exception:
            logger.exception("Account recovery background task failed")
        finally:
            # This thread opened its own database connection; close it.
            connection.close()
            _backgroundQueue.task_done()


def _startWorkers():
    with _workersLock:
        while len(_workers) < BACKGROUND_WORKERS:
            thread = threading.Thread(target=_worker)
            # Daemon, so a stuck mail server cannot hold up a process shutdown.
            # Work queued or in flight at that moment is lost; the user can ask
            # again.
            thread.daemon = True
            thread.start()
            _workers.append(thread)


def _runInWorkers(func, *args):
    """Queue func(*args) for a worker thread. If the queue is full, the work is
    dropped and logged; the caller's response does not change either way."""
    _startWorkers()
    try:
        _backgroundQueue.put_nowait((func, args))
    except Queue.Full:
        logger.error("Account recovery background queue is full; dropped %s" % func.__name__)


# Runs work after the response has been sent. Tests replace it to run inline.
runInBackground = _runInWorkers


def _stripe(action, keyHash):
    return int(hashlib.sha1(action + '|' + keyHash).hexdigest()[:8], 16) % LOCK_STRIPES


def _ensureLockRows(stripes):
    """Create any missing lock rows. Migration 0013 creates all of them; this
    only matters for a database built without migrations (such as tests).
    There are at most LOCK_STRIPES rows, so this cannot grow the table."""
    existing = set(AccountRecoveryLock.objects.filter(stripe__in=stripes).values_list('stripe', flat=True))
    for stripe in stripes:
        if stripe in existing:
            continue
        try:
            with transaction.atomic():
                AccountRecoveryLock.objects.create(stripe=stripe)
        except IntegrityError:
            pass


def reserve(limits):
    """Count one request against each of the given limits, atomically.

    limits: list of ((action, maxCount), key). Returns True and records the
    request if every limit has room; returns False and records nothing if any
    limit is used up.

    Checking the counts and recording the attempt must be one step: otherwise
    two requests can both read count == max - 1 and both pass. So the request
    locks the lock rows for its keys (in a fixed order, to avoid deadlocks),
    then counts and records while holding them. Requests that share a key
    always share its lock row, so they run one at a time.
    """
    now = timezone.now()
    maxCounts = {}
    for (action, maxCount), key in limits:
        k = (action, _hashKey(key))
        maxCounts[k] = min(maxCount, maxCounts.get(k, maxCount))
    keys = sorted(maxCounts)
    stripes = sorted(set(_stripe(action, keyHash) for action, keyHash in keys))

    reserved = None
    # Retry when MySQL picks this transaction as a deadlock or lock-wait victim.
    for _attempt in range(MAX_TRIES):
        try:
            reserved = _reserveOnce(keys, stripes, maxCounts, now)
        except OperationalError as e:
            if not e.args or e.args[0] not in RETRYABLE_MYSQL_ERRORS:
                raise
            logger.warning("Account recovery reserve retrying after MySQL error %s" % e.args[0])
            reserved = None
        if reserved is not None:
            break

    if reserved is None:
        # Could not get the locks; refuse rather than skip the limit.
        return False
    try:
        _purge(now)
    except OperationalError:
        # Cleanup only; the next request will try again.
        logger.exception("Account recovery purge failed")
    return reserved


def _reserveOnce(keys, stripes, maxCounts, now):
    """One locking pass. Returns True/False, or None if a lock row was missing."""
    since = now - RATE_LIMIT_WINDOW
    _ensureLockRows(stripes)
    with transaction.atomic():
        for stripe in stripes:
            if not list(AccountRecoveryLock.objects.select_for_update().filter(stripe=stripe)):
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
        return True


def _purge(now):
    AccountRecoveryAttempt.objects.filter(createdAt__lt=now - RETENTION).delete()


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
