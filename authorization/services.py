import requests
import json
from models import Status

class SubscriptionService():
    @staticmethod
    def check(ipAddress,partyId,partnerId, hostUrl):
        if ipAddress == None and partyId == None:
            return False
        requestUrl = '%s/subscriptions/active/?partnerId=%s' % (hostUrl,partnerId)
        if not partyId == None:
            requestUrl += '&partyId=%s' % (partyId)
        if not ipAddress == None:
            requestUrl += '&ip=%s' % (ipAddress)
        response = requests.get(requestUrl)
        contentJson = json.loads(response.content)

        return contentJson['active']

class AuthenticationService():
    @staticmethod
    def check(loginKey,partyId, partnerId, hostUrl):
        if partyId == None:
            return False
        if loginKey == None:
            return False
        if partyId == None:
            return False
        requestUrl = '%s/users/login/' % (hostUrl)
        cookies = {'partyId':partyId, 'secret_key':loginKey}
        response = requests.get(requestUrl, cookies=cookies)

        try:
            contentJson = json.loads(response.content)
        except Exception, e:
            # currently Authentication service returns {login:True} if authenticated,
            # and returns an html if not. TODO: make authentication service return something
            # that is more intuitive.
            return False
        return contentJson['bool']

