# PWL-1036: helpers for the unauthenticated account-recovery endpoints
# (/credentials/resetPwd/ and /credentials/getUsernames/).

import hashlib
from datetime import timedelta

from django.utils import timezone

from authentication.models import AccountRecoveryAttempt
from common.common import getRemoteIpAddress

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


def _hashKey(value):
    if isinstance(value, unicode):
        value = value.encode('utf-8')
    return hashlib.sha1(value).hexdigest()


def clientIp(request):
    return getRemoteIpAddress(request) or 'unknown'


def isRateLimited(limits):
    """limits: list of ((action, maxCount), key). True if any limit is used up."""
    since = timezone.now() - RATE_LIMIT_WINDOW
    for (action, maxCount), key in limits:
        count = AccountRecoveryAttempt.objects.filter(
            action=action, keyHash=_hashKey(key), createdAt__gte=since).count()
        if count >= maxCount:
            return True
    return False


def recordAttempt(limits):
    """Count one accepted request against each of the given limits."""
    now = timezone.now()
    AccountRecoveryAttempt.objects.bulk_create([
        AccountRecoveryAttempt(action=action, keyHash=_hashKey(key), createdAt=now)
        for (action, _maxCount), key in limits
    ])
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
