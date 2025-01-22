# utility class for authenticating and calling CyVerse API

from paywall2 import settings
import requests, json
from subscription.models import UsageAddonPurchaseSync

class CyVerseClient(object):

    def __init__(self):
        self.authUrl = settings.CYVERSE_AUTH_URL
        self.clientId = settings.CYVERSE_CLIENT_ID
        self.clientSecret = settings.CYVERSE_SECRET
        self.domain = settings.CYVERSE_DOMAIN
        self.apiUrl = settings.CYVERSE_API_URL
        self.addOnApiUrl = settings.CYVERSE_ADDON_API_URL

    def getAuthHeader(self):
        try:
            authToken = self.getAuthToken()
            return {
                "Authorization" : "Bearer " + authToken
            }
        except RuntimeError as error:
            raise

    def getAuthToken(self):
        data = {
            "grant_type":"client_credentials"
        }
        response = requests.post(self.authUrl, data=data, auth=(self.clientId, self.clientSecret))
        if response.status_code == 200:
            contentObj = json.loads(response.content)
            return contentObj.get('access_token')
        else:
            contentObj = json.loads(response.content)
            errMsg = "Error getting authentication token: status_code: %s; error: %s; message: %s" % (
                response.status_code, contentObj.get("error", "N/A"), contentObj.get("error_description", "N/A"))
            raise RuntimeError(errMsg)

    def postTierPurchase(self, username, purchaseTier, durationInDays):
        # Determine the period value based on the duration
        if durationInDays == 365:
            period = 1
        elif durationInDays == 730:
            period = 2
        else:
            period = None
        
        # Update the URL to include the period parameter
        url = "%s/%s?periods=%s" % (self.apiUrl % username, purchaseTier, period)
        
        try:
            headers = self.getAuthHeader()
            response = requests.put(url, headers=headers)
            contentObj = json.loads(response.content)
            if response.status_code != 200:
                errMsg = "Error posting usage tier purchase to %s. status_code: %s; status: %s; message: %s" % (
                    url, response.status_code, contentObj.get("status", "N/A"), contentObj.get("error", "N/A"))
                raise RuntimeError(errMsg)
        except RuntimeError as error:
            raise

    def getSubscriptionTier(self, username):
        url = self.apiUrl % (username)
        try:
            headers = self.getAuthHeader()
            response = requests.get(url, headers=headers)
            contentObj = json.loads(response.content)
            if response.status_code != 200:
                errMsg = "Error getting usage tier purchase from %s. status_code: %s; status: %s; message: %s" % (
                    url, response.status_code, contentObj.get("status", "N/A"), contentObj.get("error", "N/A"))
                raise RuntimeError(errMsg)
            return {
                'tier': contentObj['result']['plan']['name'],
                'uuid': contentObj['result']['id'],
                'endDate': contentObj['result']['effective_end_date']
            }
        except RuntimeError as error:
            raise

    def getAddonPurchases(self, subscriptionUUID):
        url = self.addOnApiUrl % subscriptionUUID
        try:
            headers = self.getAuthHeader()
            response = requests.get(url, headers=headers)
            contentObj = json.loads(response.content)
            if response.status_code != 200:
                errMsg = "Error getting add on purchases from %s. status_code: %s; status: %s; message: %s" % (
                    url, response.status_code, contentObj.get("status", "N/A"), contentObj.get("error", "N/A"))
                raise RuntimeError(errMsg)
            result =[]
            for item in contentObj['subscription_addons']:
                result.append({
                    'uuid': item['uuid'],
                    'option-name': item['addon']['name'],
                    'option-uuid': item['addon']['uuid']
                    })
            return result
        except RuntimeError as error:
            raise

    def postAddonPurchase(self, subscriptionUUID, optionUUID):
        url = self.addOnApiUrl % subscriptionUUID
        try:
            headers = self.getAuthHeader()
            response = requests.post(url, headers=headers, json={"uuid": optionUUID})
            contentObj = json.loads(response.content)
            if response.status_code != 200:
                errMsg = "Error posting add on purchase to %s. status_code: %s; status: %s; message: %s" % (
                    url, response.status_code, contentObj.get("status", "N/A"), contentObj.get("error", "N/A"))
                raise RuntimeError(errMsg)
            return contentObj['subscription_addon']['uuid']
        except RuntimeError as error:
            raise

    def getAddonOptions(self):
        url = "%s/terrain/service/qms/addons" % self.domain
        try:
            headers = self.getAuthHeader()
            response = requests.get(url, headers=headers)
            contentObj = json.loads(response.content)
            if response.status_code != 200:
                errMsg = "Error getting add on options from %s. status_code: %s; status: %s; message: %s" % (
                    url, response.status_code, contentObj.get("status", "N/A"), contentObj.get("error", "N/A"))
                raise RuntimeError(errMsg)
            return contentObj['addons']
        except RuntimeError as error:
            raise

    def testPayment(self):
        url = "http://localhost/subscriptions/payments/usage-tier/"
        data={
            "price": 590,
            "stripeToken": '123',
            "username": "xingguo",
            "email": "xingguo.chen@arabidopsis.org",
            "firstName": "Xingguo",
            "lastName": "Chen",
            "institute": "Phoenix Bioinformatics",
            "street": "1612 Koch Ln",
            "city": "San Jose",
            "state": "CA",
            "country": "USA",
            "zip": 95125,
            "redirect": "",
            "other": "Other info",
            "cardLast4": "3414",
            "domain": "https://cyverse.org/",
            "subscription": json.dumps({
                "subscription": {
                    "tierId": 2
                },
                "addons":[{
                    "optionId": 1,
                    "purchaseQty": 2,
                    "subscriptionUUID": "8cc5cdc4-ce6c-11ed-ab1d-62d47aced14b",
                    "expirationDate": "2024-03-29T13:01:53.18892-07:00",
                    "chargeAmount": 250
                }]
            })
        }
        response = requests.post(url, data=data)
        if response.status_code != 200:
            errMsg = "Error post payments to %s. status_code: %s; " % (
                url, response.status_code)
  
# run test by
# echo -e "from common.utils.cyverseUtils import test\ntest()" | ./manage.py shell
def test():
    # test for 1. invalid auth token
    # 2. invalid user
    # 3. invalid tier
    # 4. normal purchase
    client = CyVerseClient()

    # test for invalid user. Note that API does not return error for invalid username
    # try:
    #     client.postTierPurchase('xingguoxxx', 'Pro')
    # except RuntimeError as error:
    #     print error

    # # test for invalid purchase tier
    # try:
    #     client.postTierPurchase('xingguo', 'Test')
    # except RuntimeError as error:
    #     print error

    # # test for normal purchase
    # try:
    #     client.postTierPurchase('xingguo', 'Pro')
    # except RuntimeError as error:
    #     print error

    # test for invalid authentication token
    # try:
    #     client.clientSecret = '123'
    #     client.postTierPurchase('xingguo', 'Test')
    # except RuntimeError as error:
    #     print error

    # # test for getting purchase UUID
    try:
        # client.testPayment()
        # client.postTierPurchase('xingguo', 'Basic')
        subscription = client.getSubscriptionTier('xingguo')
        print(subscription)
        print(client.getAddonPurchases(subscription['uuid']))
        print(client.getAddonOptions())
        # print(client.getSubscriptionTier('shabari'))
        # print(client.getSubscriptionTier('edwins'))
        # print(client.getSubscriptionTier('elyons'))
        # print(client.getSubscriptionTier('sriram'))
    except RuntimeError as error:
        print error

    # test for getting add on options
    # try:
    #     print(client.getAddonOptions())
    # except RuntimeError as error:
    #     print error
