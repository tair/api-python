
#import Path, AccessType
from models import Status, AccessType
from subscription.models import Subscription
from authentication.models import Credential

class Authorization:
    @staticmethod
    def getAccessStatus(loginKey, ip, partyId, url, partnerId, hostUrl, apiKey,
                       matching_rules=None, parties=None):
        if matching_rules is None:
            matching_rules = AccessType.getMatchingRules(url, partnerId)
        if not Authorization.authentication(loginKey, partyId, url, partnerId, hostUrl, apiKey,
                                           matching_rules=matching_rules):
            return Status.needLogin
        if not Authorization.subscription(ip, partyId, url, partnerId, hostUrl, apiKey,
                                          matching_rules=matching_rules, parties=parties):
            return Status.needSubscription
        return Status.ok

    @staticmethod
    def subscription(ip, partyId, url, partnerId, hostUrl, apiKey,
                     matching_rules=None, parties=None):
        if matching_rules is not None:
            if not matching_rules.get("Paid", False):
                return True
        else:
            if not AccessType.checkHasAccessRule(url, "Paid", partnerId):
                return True
        if Authorization.hasActiveSubscription(ip, partyId, partnerId, parties=parties):
            return True
        return False

    @staticmethod
    def hasActiveSubscription(ip, partyId, partnerId, parties=None):
        if partyId and partyId.isdigit() and len(Subscription.getActiveById(partyId, partnerId)) > 0:
            return True
        if parties is not None:
            if len(Subscription.getActiveByParties(parties, partnerId)) > 0:
                return True
        elif ip and len(Subscription.getActiveByIp(ip, partnerId)) > 0:
            return True
        return False

    @staticmethod
    def authentication(loginKey, partyId, url, partnerId, hostUrl, apiKey, matching_rules=None):
        if matching_rules is not None:
            if not matching_rules.get("Login", False):
                return True
        else:
            if not AccessType.checkHasAccessRule(url, "Login", partnerId):
                return True
        if Credential.validate(partyId, loginKey):
            return True
        return False
