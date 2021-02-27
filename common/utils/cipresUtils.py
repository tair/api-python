# utility class for decrypt partner CIPRES's user password
# install dependency: pip install pycrypto

from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256, SHA512, HMAC
from Crypto.Cipher import AES
from Crypto import Random
from paywall2 import settings
from django.utils import timezone

import base64, hmac, hashlib, codecs, requests

class AESCipher(object):

    def __init__(self): 
        # charset
        self.charset = "utf-8"
        # constants for secret key
        self.clientSecret = settings.CIPHER_CLIENT_SECRET
        self.salt = settings.CIPHER_SALT
        self.iteration = settings.CIPHER_ITERATION
        self.keyLength = 32 # in bytes, = 256 bits
        # constants for decrpytion
        self.mode = AES.MODE_CBC
        self.blockSize = AES.block_size # 16 bytes

    def getKey(self):
        key = hashlib.pbkdf2_hmac(
            'sha512', # The hash digest algorithm for HMAC
            bytearray(self.clientSecret),
            base64.urlsafe_b64decode(self.salt + b'==='), # handles padding issue
            self.iteration, # It is recommended to use at least 100,000 iterations of SHA-256 
            self.keyLength # Get a 128 byte key
        )
        # print base64.b64encode(key)
        return key

    def encrypt(self, raw):
        secretKey = self.getKey()
        padded = self._pad(raw.encode(self.charset))
        iv = Random.new().read(self.blockSize)
        cipher = AES.new(secretKey, self.mode, iv)
        return base64.b64encode(iv + cipher.encrypt(padded))

    # throws TypeError for incorrectly padded encryptedMsg
    def decrypt(self, encryptedMsg):
        secretKey = self.getKey()
        msgArray = base64.b64decode(encryptedMsg + b'===') # handles padding issue
        iv = msgArray[:self.blockSize]
        cipher = AES.new(secretKey, self.mode, iv)
        return self._unpad(cipher.decrypt(msgArray[self.blockSize:])).decode(self.charset)

    # add padding
    def _pad(self, s):
        return s + (self.blockSize - len(s) % self.blockSize) * chr(self.blockSize - len(s) % self.blockSize)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

class APICaller(object):
    def __init__(self): 
        # constants for secret key
        self.apiBaseUrl = settings.CIPRES_API_BASE_URL
        self.basicAuthToken = settings.CIPRES_BASIC_AUTH_TOKEN
        self.accessToken = settings.CIPRES_ACCESS_TOKEN

    def getAuthHeader(self):
        authToken = "Basic " + str(self.basicAuthToken)
        return {
            "Authorization" : authToken,
            "X-CIPRES-TOKEN" : self.accessToken
        }

    # succeed status code: 201
    # succeed response body:
    # {
    #     "user_id":"33ac7587-eb4d-49f0-a481-f12178efdd71",
    #     "username":"xingguo",
    #     "first_name":"Xingguo",
    #     "last_name":"Chen",
    #     "email":"xingguo.chen@phoenixbioinformatics.org",
    #     "institution":"Phoenix Bioinformatics",
    #     "country":"US",
    #     "active":true
    # }
    def getUserInfo(self, userIdentifier):
        url = self.apiBaseUrl + '/v1/user/' + userIdentifier
        headers = self.getAuthHeader()
        response = requests.get(url, headers=headers)
        return response

    # succeed status code: 200
    # succeed response body: {"su":0}
    def getUserUsage(self, userIdentifier):
        url = self.apiBaseUrl + '/v1/su/user/' + userIdentifier
        headers = self.getAuthHeader()
        response = requests.get(url, headers=headers)
        return response

    # succeed status code: 201
    # succeed response body:
    # {
    #     "user_uuid" : "33ac7587-eb4d-49f0-a481-f12178efdd71",
    #     "su_amount" : 1000,
    #     "transaction_time" : "2020-10-29 04:39:23",
    #     "transaction_number" : "ch_1Gd2JxDbkoAs09FVq4snGANj",
    #     "transaction_type" : "Purchase"
    # }
    # sample failed status code: 500 (caused by duplicated transaction_id)
    # sample failed response body:
    # {
    #     "code":"INTERNAL_ERROR",
    #     "message":"Internal error occured.",
    #     "resource":"v1/user/su",
    #     "request_id":"bfd1c1a1-0ca1-460f-a723-20fefc331f47"
    # }
    def postUnitPurchase(self, userIdentifier, unitQty, transactionId, purchaseTime):
        url = self.apiBaseUrl + '/v1/user/su'
        print(url)
        headers = self.getAuthHeader()
        time = purchaseTime.strftime("%Y-%m-%dT%H:%M:%S")
        data = {
            "user_id":userIdentifier,
            "su":unitQty,
            "transaction_id":transactionId,
            "transaction_time": time
        }
        response = requests.post(url, headers=headers, data=data)
        return response

# run test by
# ./manage.py shell
# from common.utils.cipresUtils import test
# test()
def test():
    ## cipher test
    cipher = AESCipher()

    # test encryption and decryption with UTF-8 char
    raw = u'123\u212BM54@'
    print "raw"
    print raw.encode(cipher.charset)
    encrypted = cipher.encrypt(raw)
    print "encrypted"
    print encrypted
    decrypted = cipher.decrypt(encrypted)
    print "decrypted"
    print decrypted.encode(cipher.charset)
    print "decrypted chars in hex"
    for c in decrypted: 
        print hex(ord(c))
    hashed = hashlib.sha1(decrypted.encode(cipher.charset)).hexdigest()
    print "hashed"
    print hashed

    ## test encryption
    # raw = "PW@666.cipres"
    # encryptedMsg = cipher.encrypt(raw)
    # print raw
    # print encryptedMsg
    # print cipher.decrypt(encryptedMsg)

    ## api call test
    # caller = APICaller()
    # userIdentifier = "33ac7587-eb4d-49f0-a481-f12178efdd71"

    # getUserInfoResponse = caller.getUserInfo(userIdentifier)
    # print(getUserInfoResponse.status_code)
    # print(getUserInfoResponse.text)

    # getUserUsageResponse = caller.getUserUsage(userIdentifier)   
    # print(getUserUsageResponse.status_code)
    # print(getUserUsageResponse.text)

    ## note this transactionId can only be used once
    # transctionId = 'ch_1Gd2JxDbkoAs09FVq4snGjPk'
    # postUnitPurchasePostResponse = caller.postUnitPurchase(userIdentifier, 1000, transactionId, timezone.now())
    # print(postUnitPurchasePostResponse.status_code)
    # print(postUnitPurchasePostResponse.text)




