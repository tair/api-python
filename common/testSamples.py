from apikey.models import ApiKey
from partner.models import Partner
from party.models import Party
import copy

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

class CommonCredentialSample():
    url = None
    serverUrl = None
    path = 'credentials/'
    loginPath = 'credentials/login/'
    USERNAME = 'phoenix_admin'
    FIRSTNAME = 'Phoenix'
    LASTNAME = 'Bioinformatics'
    PASSWORD = 'phoenix123'
    EMAIL = 'info@phoenixbioinformatics.org'
    INSTITUTION = 'Phoenix Bioinformatics'
    USER_IDENTIFIER = 123
    data = {
        'username': USERNAME,
        'firstName': FIRSTNAME,
        'lastName': LASTNAME,
        'name': '%s %s' % (FIRSTNAME, LASTNAME),
        'password': PASSWORD,
        'email': EMAIL,
        'institution': INSTITUTION,
        'partnerId': None,
        'userIdentifier': USER_IDENTIFIER
    }

    def __init__(self, serverUrl):
        self.serverUrl = serverUrl
        self.url = serverUrl + self.path

    def setPartnerId(self, partnerId):
        self.data['partnerId'] = partnerId

    def getLoginUrl(self):
        return self.serverUrl + self.loginPath + '?partnerId=%s' % self.data['partnerId']

    def getLoginData(self):
        return {
            'user': self.data['username'],
            'password': self.data['password']
        }