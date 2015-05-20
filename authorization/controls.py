
#import Path, AccessType
from services import MeteringService, SubscriptionService
from models import Status, AccessType

class Authorization:
    @staticmethod
    def getAccessStatus(ip, partyId, url, partnerId):
        status = Status.ok
        meterStatus = MeteringService.checkByIp(ip, partnerId)
        if meterStatus == Status.ok:
            status = Status.ok
        else:
            # metered, check subscription.
            if Authorization.subscription(ip, partyId, url, partnerId):
                # metered but has subscription, return OK.
                status = Status.ok
            else:
                # metered and does not have subscription.
                # return warn or block depend on status
                if meterStatus == Status.meterWarn:
                    status = Status.meterWarn
                else:
                    status = Status.needSubscription
        return status

    @staticmethod
    def subscription(ip, partyId, url, partnerId):
        accessType = AccessType.getByUrl(url, partnerId)
        if not accessType == "Paid":
            # free content, allow access.
            return True

        if SubscriptionService.checkByIp(ip, partnerId) or \
           SubscriptionService.checkById(partyId, partnerId):
            # if either party is subscribed either by IP or partyId,
            # then allow access. Else, deny.
            return True
        return False
