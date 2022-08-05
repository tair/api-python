from apikey.models import ApiKey
from partner.models import Partner
from party.models import Party
from authentication.models import Credential
import copy
import hashlib

def forcePost(model, pkName, data):
    u = model(**data)
    u.save()
    return u.__dict__[pkName]

class CommonApiKeySample():
    data = {
        'apiKey':'testKey',
    }
    pkName = 'apiKeyId'
    model = ApiKey

    def forcePost(self,data):
        return forcePost(self.model, self.pkName, data)

class CommonPartnerSample():
    url = None
    path = 'partners/'
    data = {
        'partnerId':'phoenix',
        'name':'PhoenixBio',
    }
    pkName = 'partnerId'
    model = Partner

    def __init__(self, serverUrl):
        self.url = serverUrl + self.path

    def forcePost(self,data):
        return forcePost(self.model, self.pkName, data)

class CommonUserPartySample():
    path = 'parties/'
    url = None
    data = {
        'partyType':'user',
        'name':'phoenix_admin',
    }
    pkName = 'partyId'
    model = Party

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        return forcePost(self.model, self.pkName, data)

class CommonCredentialSample():
    url = None
    path = 'credentials/'
    USERNAME = 'phoenix_admin'
    FIRSTNAME = 'Phoenix'
    LASTNAME = 'Bioinformatics'
    PASSWORD = 'phoenix123'
    EMAIL = 'info@phoenixbioinformatics.org'
    INSTITUTION = 'Phoenix Bioinformatics'
    USER_IDENTIFIER = 1
    data = {
        'username': USERNAME,
        'firstName': FIRSTNAME,
        'lastName': LASTNAME,
        'password': PASSWORD,
        'email': EMAIL,
        'institution': INSTITUTION,
        'userIdentifier': USER_IDENTIFIER,
        'partnerId': None,
        'partyId': None
    }
    pkName = 'id'
    model = Credential

    def __init__(self, serverUrl):
        self.url = serverUrl + self.path

    def setPartnerId(self, partnerId):
        self.data['partnerId'] = partnerId

    def setPartyId(self, partyId):
        self.data['partyId'] = partyId

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partyId'] = Party.objects.get(partyId=self.data['partyId'])
        postData['partnerId'] = Partner.objects.get(partnerId=self.data['partnerId'])
        postData['password'] = self.hashPassword(self.data['password'])
        return forcePost(self.model, self.pkName, postData)

    def hashPassword(self, password):
        return Credential.generatePasswordHash(password)

    def getSecretKey(self):
        # this has dependency on authentication.views regarding argument
        return Credential.generateSecretKey(self.data['partyId'], self.hashPassword(self.data['password']))
