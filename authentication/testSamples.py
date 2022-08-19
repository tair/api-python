import django
import hashlib
import copy
from authentication.models import Credential
from partner.models import Partner
from party.models import Party
from common.tests import TestGenericInterfaces

genericForcePost = TestGenericInterfaces.forcePost

class CredentialSample():
    path = 'credentials/'
    loginPath = 'credentials/login/'
    serverUrl = None
    url = None
    USERNAME = 'test_user'
    FIRSTNAME = 'Phoenix'
    LASTNAME = 'Bioinformatics'
    PASSWORD = 'phoenix123'
    PASSWORD_UPDATE = 'phoenix456'
    EMAIL = 'techteam@arabidopsis.org'
    EMAIL_UPDATE = 'techteam@phoenixbioinformatics.org'
    INSTITUTION = 'Phoenix Bioinformatics'
    USER_IDENTIFIER = 123
    USER_IDENTIFIER_UPDATE = 124
    data = {
        'username': USERNAME,
        'firstName': FIRSTNAME,
        'lastName': LASTNAME,
        'password': PASSWORD,
        'email': EMAIL,
        'institution': INSTITUTION,
        'partyId': None,
        'partnerId': None,
        'userIdentifier': USER_IDENTIFIER
    }
    updateData = {
        'username': USERNAME + '_update',
        'firstName': FIRSTNAME + '_update',
        'lastName': LASTNAME + '_update',
        'password': PASSWORD_UPDATE,
        'email': EMAIL_UPDATE,
        'institution': INSTITUTION + ' Update',
        'partyId': None,
        'partnerId': None,
        'userIdentifier': USER_IDENTIFIER_UPDATE
    }
    updateData_no_pwd = {
        'username': USERNAME + '_update',
        'firstName': FIRSTNAME + '_update',
        'lastName': LASTNAME + '_update',
        'email': EMAIL_UPDATE,
        'institution': INSTITUTION + ' Update',
        'partyId': None,
        'partnerId': None,
        'userIdentifier': USER_IDENTIFIER_UPDATE
    }
    updateData_invalid = {
        'username': USERNAME + '_update',
        'firstName': True,
        'lastName': LASTNAME + '_update',
        'password': PASSWORD_UPDATE,
        'email': EMAIL_UPDATE,
        'institution': INSTITUTION + ' Update',
        'partyId': None,
        'partnerId': None,
        'userIdentifier': USER_IDENTIFIER_UPDATE
    }
    pkName = 'id'
    model = Credential

    def __init__(self, serverUrl):
        self.serverUrl = serverUrl
        self.url = serverUrl + self.path
        self.data = copy.deepcopy(self.data)

    def setAsUpdateExample(self):
        for key in self.data:
            if self.updateData[key]:
                self.data[key] = self.updateData[key]

    def setPartnerId(self, partnerId):
        self.data['partnerId'] = partnerId

    def setPartyId(self, partyId):
        self.data['partyId'] = partyId

    def getUserIdentifier(self):
        return self.data['userIdentifier']

    def getUsername(self):
        return self.data['username']

    def getEmail(self):
        return self.data['email']

    def getPartyId(self):
        return self.data['partyId']

    # data to submit to POST API to create credential without party
    def getDataForCreate(self):
        dataForCreate = copy.deepcopy(self.data)
        del dataForCreate['partyId']
        dataForCreate['name'] = '%s %s' % (self.data['firstName'], self.data['lastName'])
        return dataForCreate

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partyId'] = Party.objects.get(partyId=self.data['partyId'])
        postData['partnerId'] = Partner.objects.get(partnerId=self.data['partnerId'])
        postData['password'] = self.hashPassword(self.data['password'])
        return genericForcePost(self.model, self.pkName, postData)

    def hashPassword(self, password):
        return Credential.generatePasswordHash(password)

    def getLoginUrl(self):
        return self.serverUrl + self.loginPath + '?partnerId=%s' % self.data['partnerId']

    def getLoginData(self):
        return {
            'user': self.data['username'],
            'password': self.data['password']
        }

    def getSecretKey(self):
        # this has dependency on authentication.views regarding argument
        return Credential.generateSecretKey(self.data['partyId'], self.hashPassword(self.data['password']))
