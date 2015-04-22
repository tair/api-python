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
        if ipAddress == None:
            # fails IP check if no IP is provided
            return Status.blockBySubscription

        requestUrl = '%s/active/?ip=%s' % (SubscriptionService.serviceUrl, ipAddress)
        response = requests.get(requestUrl)
        contentJson = json.loads(response.content)

        if contentJson['active']:
            return Status.ok
        else:
            return Status.blockBySubscription

    @staticmethod
    def checkById(partyId):
        if partyId == None:
            #fails ID check if no partyId is provided
            return Status.blockBySubscription

        requestUrl = '%s/active/?partyId=%s' % (SubscriptionService.serviceUrl, partyId)
        response = requests.get(requestUrl)
        contentJson = json.loads(response.content)

        if contentJson['active']:
            return Status.ok
        else:
            return Status.blockBySubscription
