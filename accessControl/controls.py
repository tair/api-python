
#import Path, AccessType
from services import MeteringService, SubscriptionService
from models import Status

class AccessControl:
    @staticmethod
    def execute(ip, url):
        accessType = "paid"
        if accessType == "free":
            return Status.ok
        elif accessType == "paid":
            status = AccessControl.checkSubscription(ip)
            if not status == Status.ok:
                return status

        #passes all checks, allow access
        return Status.ok
    
    @staticmethod
    def checkSubscription(ip):
        #check metering status to see if user is blocked
        meterStatus = MeteringService.checkByIp(ip)
        if meterStatus == Status.ok or meterStatus == Status.warn:
            return meterStatus

        print "checking subscription"
        #blocked, check subscription
        return SubscriptionService.checkByIp(ip)
        
