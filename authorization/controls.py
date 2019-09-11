
#import Path, AccessType
from .models import Status, AccessType
from subscription.models import Subscription
from authentication.models import Credential

class Authorization:
    @staticmethod
    def getAccessStatus(loginKey, ip, partyId, url, partnerId, hostUrl, apiKey):
        # check login
        if not Authorization.authentication(loginKey, partyId, url, partnerId, hostUrl, apiKey):
            return Status.needLogin

        # no login required or is already logged in, check subscription
        if not Authorization.subscription(ip, partyId, url, partnerId, hostUrl, apiKey):
            return Status.needSubscription

        # passes both login and subscription check. OK to access
        return Status.ok

    @staticmethod
    def subscription(ip, partyId, url, partnerId, hostUrl, apiKey):
        if not AccessType.checkHasAccessRule(url, "Paid", partnerId):
            # does not have Paid access rule to this url, allow access.
            return True
        if Authorization.hasActiveSubscription(ip, partyId, partnerId):
            # have subscription, allow access.
            return True
        return False

    @staticmethod
    def hasActiveSubscription(ip, partyId, partnerId):
        if partyId and partyId.isdigit() and len(Subscription.getActiveById(partyId, partnerId)) > 0:
            return True
        if ip and len(Subscription.getActiveByIp(ip, partnerId)) > 0:
            return True
        return False

    @staticmethod
    def authentication(loginKey, partyId, url, partnerId, hostUrl, apiKey):
        if not AccessType.checkHasAccessRule(url, "Login", partnerId):
            # does not have Login access rule to this url, allow access.
            return True
        if Credential.validate(partyId, loginKey):
            # have authentication, allow access.
            return True
        return False
