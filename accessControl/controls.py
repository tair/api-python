
#import Path, AccessType
from services import MeteringService, SubscriptionService
from models import Status, AccessType

class AccessControl:
    @staticmethod
    def execute(ip, partyId, url):
        accessType = AccessType.getByUrl(url)
        if accessType == "Free":
            return Status.ok
        elif accessType == "Paid":
            status = AccessControl.checkSubscription(ip, partyId)
            if not status == Status.ok:
                return status

        #passes all checks, allow access
        return Status.ok

    
    @staticmethod
    def checkSubscription(ip, partyId):
        #check metering status. Allow access if status is ok or warn
        meterStatus = MeteringService.checkByIp(ip)
        if meterStatus == Status.ok or meterStatus == Status.warn:
            return meterStatus

        #blocked, check subscription. Allow access if either IP 
        #or partyId has an active subscription.
        if SubscriptionService.checkByIp(ip) == Status.ok or \
           SubscriptionService.checkById(partyId) == Status.ok:
            return Status.ok
        
        #blocks user if it fails both metering and subscription check
        return Status.blockBySubscription
