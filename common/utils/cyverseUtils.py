# utility class for authenticating and calling CyVerse API

from paywall2 import settings
import requests, json

class CyVerseClient(object):

    def __init__(self):
        self.authUrl = settings.CYVERSE_AUTH_URL
        self.clientId = settings.CYVERSE_CLIENT_ID
        self.clientSecret = settings.CYVERSE_SECRET
        self.apiUrl = settings.CYVERSE_API_URL

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

    def postUnitPurchase(self, username, purchaseTier):
        url = self.apiUrl % (username, purchaseTier)
        try:
            headers = self.getAuthHeader()
            response = requests.put(url, headers=headers)
            if response.status_code != 200:
                contentObj = json.loads(response.content)
                errMsg = "Error posting usage tier purchase to %s. status_code: %s; status: %s; message: %s" % (
                    url, response.status_code, contentObj.get("status", "N/A"), contentObj.get("error", "N/A"))
                raise RuntimeError(errMsg)
        except RuntimeError as error:
            raise


# run test by
# ./manage.py shell
# from common.utils.cyverseUtils import test
# test()
def test():
    # test for 1. invalid auth token
    # 2. invalid user
    # 3. invalid tier
    # 4. normal purchase
    client = CyVerseClient()

    # test for invalid user. Note that API does not return error for invalid username
    try:
        client.postUnitPurchase('xingguoxxx', 'Pro')
    except RuntimeError as error:
        print error

    # test for invalid purchase tier
    try:
        client.postUnitPurchase('xingguo', 'Test')
    except RuntimeError as error:
        print error

    # test for normal purchase
    try:
        client.postUnitPurchase('xingguo', 'Pro')
    except RuntimeError as error:
        print error

    # test for invalid authentication token
    try:
        client.clientSecret = '123'
        client.postUnitPurchase('xingguo', 'Test')
    except RuntimeError as error:
        print error


