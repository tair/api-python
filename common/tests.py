import json
import sys
import time
# Python 3: library urllib -> urllib.parse
import urllib
from testSamples import CommonApiKeySample, CommonPartnerSample, CommonUserPartySample, CommonCredentialSample
from partner.models import Partner
from apikey.models import ApiKey
from django.test import Client
from django.conf import settings
# Python 3: module Cookie -> http.cookies
from Cookie import SimpleCookie

class TestGenericInterfaces:
    @staticmethod
    def getHost():
        if hasattr(settings, 'HOSTNAME'):
            return settings.HOSTNAME
        # default connection to localhost
        return "http://localhost/"

    @staticmethod
    def forceGet(model, pkName, pk):
        try:
            filters = {pkName:pk}
            return model.objects.get(**filters)
        except:
            return None

    @staticmethod
    def forceDelete(model, pkName,pk):
        try:
            filters = {pkName:pk}
            model.objects.get(**filters).delete()
        except:
            pass

    @staticmethod
    def forcePost(model, pkName, data):
        u = model(**data)
        u.save()
        return u.__dict__[pkName]

class GenericTest(object):
    apiKeySample = CommonApiKeySample()
    apiKey = None

    def setUp(self):
        self.apiKeyId = self.apiKeySample.forcePost(self.apiKeySample.data)
        self.apiKey = self.apiKeySample.data['apiKey']

# create a credential record to login for every test
class LoginRequiredTest(GenericTest):
    credentialId = None
    secretKey = None

    def setUp(self):
        # self.pauseForAPIRest()
        super(LoginRequiredTest, self).setUp()
        serverUrl = TestGenericInterfaces.getHost()
        credentialSample = CommonCredentialSample(serverUrl)

        partnerSample = CommonPartnerSample(serverUrl)
        partnerId = partnerSample.forcePost(partnerSample.data)
        credentialSample.setPartnerId(partnerId)

        userPartySample = CommonUserPartySample(serverUrl)
        partyId = userPartySample.forcePost(userPartySample.data)
        credentialSample.setPartyId(partyId)

        credentialSample.forcePost(credentialSample.data)

        self.credentialId = partyId
        self.secretKey = credentialSample.getSecretKey()

    def pauseForAPIRest(self):
        time.sleep(0.5)

# This function checks if sampleData is within the array of data retrieved
# from API call.
def checkMatch(sampleData, retrievedData, pkName, pk):
    hasMatch = False
    if not isinstance(retrievedData, list):
        retrievedData = [retrievedData]
    for item in retrievedData:
        # find the entry from dataArray that has the same PK
        # as the entry created
        if item[pkName] == pk:
            hasMatch = True
            for key in sampleData:
                # makes sure that all contents from sample is the
                # same as content retrieved from request
                if not key in item or not (item[key] == sampleData[key] or compareDateTime(sampleData[key], item[key]) 
                    or float(item[key]) == float(sampleData[key])):
                    hasMatch = False
                    break
    if not hasMatch:
        print "\nERROR: sample data %s and retrieved data %s does not match" % (sampleData, retrievedData)
    return hasMatch

## This function checks if sampleData is within the array of data retrieved
# from API call, and skip common key we use for authentication, such as apiKey, 
# credential, party etc.
def filterAndCheckMatch(sampleData, retrievedDataArray, pkName, pk, commonKeyName, commonKeyValue):
    filteredArray = []
    for item in retrievedDataArray:
            if item[commonKeyName] == commonKeyValue:
                continue;
            else:
                filteredArray.append(item)
    return checkMatch(sampleData, filteredArray, pkName, pk)

def compareDateTime(sampleTime, retrievedTime):
    retrievedTime = retrievedTime.replace('T', ' ').replace('Z', '')
    return sampleTime == retrievedTime

class GenericGETOnlyTest(GenericTest):

    def test_for_get_all(self):
        sample = self.sample
        url = self.getUrl(sample.url)
        self.getAllHelper(url)

    def test_for_get(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = self.getUrl(sample.url, sample.pkName, pk) 
        if self.apiKey:
            self.client.cookies = SimpleCookie({'apiKey':self.apiKey})

        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(checkMatch(sample.data, json.loads(res.content), sample.pkName, pk), True)

    def getAllHelper(self, url, commonKeyName = None, commonKeyValue = None):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        if self.apiKey:
            self.client.cookies = SimpleCookie({'apiKey':self.apiKey})

        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        if commonKeyName and commonKeyValue:
            self.assertEqual(filterAndCheckMatch(sample.data, json.loads(res.content), sample.pkName, pk, commonKeyName, commonKeyValue), True)
        else:
            self.assertEqual(checkMatch(sample.data, json.loads(res.content), sample.pkName, pk), True)

    def getUrl(self, url, pkName = None, pk = None):
        fullUrl = url
        if pkName and pk:
            fullUrl = url + '?%s=%s' % (pkName, str(pk))
        return fullUrl

class GenericCRUDTest(GenericGETOnlyTest):

    # GET tests defined in GenericGETOnlyTest class

    def test_for_create(self):
        sample = self.sample
        url = self.getUrl(sample.url)
        if self.apiKey:
            self.client.cookies = SimpleCookie({'apiKey':self.apiKey})

        res = self.client.post(url, sample.data)

        self.assertEqual(res.status_code, 201)
        self.assertIsNotNone(TestGenericInterfaces.forceGet(sample.model,sample.pkName,json.loads(res.content)[sample.pkName]))

    def test_for_update(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = self.getUrl(sample.url, sample.pkName, pk)
        if sample.pkName in sample.updateData:
            pk = sample.updateData[sample.pkName]
        if self.apiKey:
            self.client.cookies = SimpleCookie({'apiKey':self.apiKey})

        # the default content type for put is 'application/octet-stream'
        res = self.client.put(url, json.dumps(sample.updateData), content_type='application/json')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(checkMatch(sample.updateData, json.loads(res.content), sample.pkName, pk), True)

    def test_for_delete(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = self.getUrl(sample.url, sample.pkName, pk)
        if self.apiKey:
            self.client.cookies = SimpleCookie({'apiKey':self.apiKey})
            
        res = self.client.delete(url)

        self.assertIsNone(TestGenericInterfaces.forceGet(sample.model,sample.pkName,pk))

class LoginRequiredGETOnlyTest(LoginRequiredTest, GenericGETOnlyTest):
    
    def getUrl(self, url, pkName = None, pk = None):
        secretKey = urllib.quote(self.secretKey)
        fullUrl = url + '?credentialId=%s&secretKey=%s' % (self.credentialId, secretKey)
        if pkName and pk:
            fullUrl = '%s&%s=%s' % (fullUrl, pkName, str(pk))
        return fullUrl

class LoginRequiredCRUDTest(LoginRequiredGETOnlyTest, GenericCRUDTest):
    # just inherit method from two parent classes
    pass

class ManualTest(object):
    path = ""
    testMethodStr = ""

    def test_warning(self):
        print "\n----------------------------------------------------------------------"
        print "\nWARNING: Please manually test API end point %s if necessary.\n\
        If you've \n\
        (1) upgraded Python version or\n\
        (2) upgraded Django version or\n\
        (3) updated module or setting params related to this end point\n\
        Please make sure you test this end point by %s" % (self.path, self.testMethodStr)
        print "\n----------------------------------------------------------------------"

print "using server url %s" % TestGenericInterfaces.getHost()