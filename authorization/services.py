import requests
import json
from models import Status

class MeteringService():
    serviceUrl = 'http://52.1.196.45:8000/meters'

    # Returns subscription status for a given ipAddress
    @staticmethod
    def checkByIp(ipAddress):
        if ipAddress == None:
            return Status.needSubscription

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
            status = Status.ok
        return status

class SubscriptionService():
    serviceUrl = 'http://52.1.196.45:8000/subscriptions'

    @staticmethod
    def checkByIp(ipAddress,partnerId):
        if ipAddress == None:
            return False
        requestUrl = '%s/active/?ip=%s&partnerId=%s' % (SubscriptionService.serviceUrl, ipAddress, partnerId)
        response = requests.get(requestUrl)
        contentJson = json.loads(response.content)

        return contentJson['active']

    @staticmethod
    def checkById(partyId, partnerId):
        if partyId == None:
            return False
        requestUrl = '%s/active/?partyId=%s&partnerId=%s' % (SubscriptionService.serviceUrl, partyId, partnerId)
        response = requests.get(requestUrl)
        contentJson = json.loads(response.content)

        return contentJson['active']
