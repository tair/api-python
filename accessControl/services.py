import requests
import json
from models import Status

class MeteringService():
    serviceUrl = 'http://52.1.196.45:8000/meters'

    # Returns subscription status for a given ipAddress
    @staticmethod
    def checkByIp(ipAddress):
        status = Status.ok

        #check if ip is in databse
        requestUrl = '%s/ip/%s' % (MeteringService.serviceUrl, ipAddress)
        response = requests.get(requestUrl)

        if response.status_code == 200:
            # ip is already in database, check for status
            requestUrl = '%s/ip/%s/limit' % (MeteringService.serviceUrl, ipAddress)
            response = requests.get(requestUrl)
            contentJson = json.loads(response.content)
            status = contentJson['status']
        else:
            # first time visit, normal status.
            pass
        return status

class SubscriptionService():
    serviceUrl = 'http://52.1.196.45:8000/subscriptions'

    @staticmethod
    def checkByIp(ipAddress):
        requestUrl = '%s/active/?ip=%s' % (SubscriptionService.serviceUrl, ipAddress)
        response = requests.get(requestUrl)
        contentJson = json.loads(response.content)
        print contentJson
        if len(contentJson) > 0:
            return Status.ok
        else:
            return Status.block


    
