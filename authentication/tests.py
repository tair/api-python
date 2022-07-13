#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys
import json
import copy
import urllib.request, urllib.parse, urllib.error
from django.test import TestCase, Client
from partner.testSamples import PartnerSample
from party.testSamples import UserPartySample
from common.tests import TestGenericInterfaces, GenericCRUDTest, GenericTest, ManualTest, checkMatch
from .testSamples import CredentialSample
from http.cookies import SimpleCookie

# Create your tests here.                                                                                                                                                                                 
django.setup()
serverUrl = TestGenericInterfaces.getHost()

# test for API endpoint /credentials/ and /credentials/profile/
# does not extend GenericCRUDTest class since all methods need override
class CredentialCRUDTest(GenericTest, TestCase):
    sample = CredentialSample(serverUrl)
    partnerId = None

    def setUp(self):
        super(CredentialCRUDTest,self).setUp()

        partnerSample = PartnerSample(serverUrl)
        self.partnerId = partnerSample.forcePost(partnerSample.data)
        self.sample.data['partnerId']=self.sample.updateData['partnerId']=self.partnerId

        userPartySample = UserPartySample(serverUrl)
        partyId = userPartySample.forcePost(userPartySample.data)
        self.sample.data['partyId']=self.sample.updateData['partyId']=partyId

    def test_for_create_with_party_id(self):
        sample = self.sample
        url = sample.url
        if self.apiKey:
            self.client.cookies = SimpleCookie({'apiKey':self.apiKey})

        res = self.client.post(url, sample.data)

        self.assertEqual(res.status_code, 201)
        # note the returned credential object do not contain credential table primary key "id"
        # but always contains party id instead
        self.assertIsNotNone(TestGenericInterfaces.forceGet(self.sample.model,'partyId',sample.getPartyId()))

    def test_for_create_without_party_id(self):
        sample = self.sample
        url = sample.url
        if self.apiKey:
            self.client.cookies = SimpleCookie({'apiKey':self.apiKey})

        res = self.client.post(url, sample.getDataForCreate())

        self.assertEqual(res.status_code, 201)
        # note the returned credential object do not contain credential table primary key "id"
        # but always contains party id instead
        self.assertIsNotNone(TestGenericInterfaces.forceGet(self.sample.model,'partyId',json.loads(res.content)['partyId']))

    def test_for_get(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        partnerId = self.partnerId 

        # test get by user identifier
        queryByUserIdentifier = 'userIdentifier=%s&partnerId=%s' % (sample.getUserIdentifier(), partnerId)
        self.assertGetRequestByQueryParam(queryByUserIdentifier)

        # test get by username
        queryByUsername = 'username=%s&partnerId=%s' % (sample.getUsername(), partnerId)
        self.assertGetRequestByQueryParam(queryByUsername)

        # test get by partyId
        queryByPartyId = 'partyId=%s' % sample.getPartyId()
        self.assertGetRequestByQueryParam(queryByPartyId)

    def assertGetRequestByQueryParam(self, queryParam):
        url = '%s?%s' % (self.sample.url, queryParam)
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        resObj = json.loads(res.content)
        # remove password from comparison since it is not returned in GET API
        data = copy.deepcopy(self.sample.data)
        del data['password']
        # note the returned credential object do not contain credential table primary key "id"
        # but always contains party id instead
        self.assertEqual(checkMatch(data, resObj, 'partyId', self.sample.getPartyId()), True)

    def test_for_update_by_party_id(self):
        queryParam = 'partyId=%s' % self.sample.getPartyId()
        self.runUpdateTestByQueryParam(queryParam)

    def test_for_update_by_user_identifier(self):
        queryParam = 'userIdentifier=%s&partnerId=%s' % (self.sample.getUserIdentifier(), self.partnerId)
        self.runUpdateTestByQueryParam(queryParam)

    def test_for_update_by_username(self):
        queryParam = 'username=%s&partnerId=%s' % (self.sample.getUsername(), self.partnerId)
        self.runUpdateTestByQueryParam(queryParam)

    def runUpdateTestByQueryParam(self, queryParam):
        sample = self.sample
        sample.forcePost(sample.data)
        partnerId = self.partnerId 
        loginCredential = self.getUserLoginCredential();

        url = '%s?%s&%s' % (sample.url, loginCredential, queryParam)

        # the default content type for put is 'application/octet-stream'
        # does not test for partyId update
        res = self.client.put(url, json.dumps(sample.updateData), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        resObj = json.loads(res.content)

        # hash password for comparison
        updateData = {}
        for key in sample.updateData:
            if key == 'password':
                updateData[key] = sample.hashPassword(sample.updateData[key])
            else:
                updateData[key] = sample.updateData[key]
        # manipulate sample data to match the test condition
        self.assertEqual(checkMatch(updateData, resObj, 'partyId', sample.getPartyId()), True)

    # test for API endpoint /credentials/profile/
    # this is smiliar to the UPDATE methods above except that it only accepts 
    # pratyId as query param and returns status code 201 when succeed
    def test_for_update_profile(self):
        sample = self.sample
        sample.forcePost(sample.data)
        partnerId = self.partnerId 
        loginCredential = self.getUserLoginCredential();

        url = '%scredentials/profile/?%s&partyId=%s' % (serverUrl, loginCredential, sample.getPartyId())
        # the default content type for put is 'application/octet-stream'
        # does not test for partyId update
        res = self.client.put(url, json.dumps(sample.updateData), content_type='application/json')
        # API should return 200 for an update but returns 201
        self.assertEqual(res.status_code, 201)
        resObj = json.loads(res.content)

        # hash password for comparison
        updateData = {}
        for key in sample.updateData:
            if key == 'password':
                updateData[key] = sample.hashPassword(sample.updateData[key])
            else:
                updateData[key] = sample.updateData[key]
        # manipulate sample data to match the test condition
        self.assertEqual(checkMatch(updateData, resObj, 'partyId', sample.getPartyId()), True)

    def getUserLoginCredential(self):
        sample = self.sample
        secretKey = urllib.parse.quote(sample.getSecretKey())
        return 'credentialId=%s&secretKey=%s' % (sample.getPartyId(), secretKey)

class CredentialGenericTest(TestCase):
    sample = CredentialSample(serverUrl)
    partnerId = None

    def setUp(self):
        super(CredentialGenericTest,self).setUp()

        partnerSample = PartnerSample(serverUrl)
        self.partnerId = partnerSample.forcePost(partnerSample.data)
        self.sample.data['partnerId']=self.partnerId

        userPartySample = UserPartySample(serverUrl)
        partyId = userPartySample.forcePost(userPartySample.data)
        self.sample.data['partyId']=partyId

        self.sample.forcePost(self.sample.data)

# test for API endpoint /crendetials/login/
class CredentialLoginTest(CredentialGenericTest):

    def test_for_login(self):
        loginUrl = self.sample.getLoginUrl()
        loginData = self.sample.getLoginData()
        res = self.client.post(loginUrl, loginData)
        self.assertEqual(res.status_code, 200)
        resObj = json.loads(res.content)
        self.assertIsNotNone(resObj['credentialId'])
        self.assertIsNotNone(resObj['secretKey'])

# test for API endpoint /credentials/getUsernames/
class GetUsernamesTest(CredentialGenericTest):

    def test_for_get_usernames(self):
        url = '%scredentials/getUsernames/?email=%s&partnerId=%s' % (serverUrl, self.sample.getEmail(), self.partnerId)
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        resObj = json.loads(res.content)
        # remove password from comparison since it is not returned
        data = copy.deepcopy(self.sample.data)
        del data['password']
        # note the returned credential object do not contain credential table primary key "id"
        # but always contains party id instead
        self.assertEqual(checkMatch(data, resObj, 'partyId', self.sample.getPartyId()), True)

# test for API endpoint /credentials/checkAccountExists/
class CheckAccountExistsTest(CredentialGenericTest):

    def test_for_check_account_exists(self):
        self.assertGetRequestByType('email', self.sample.getEmail())
        self.assertGetRequestByType('username', self.sample.getUsername())

    def assertGetRequestByType(self, keyName, value):
        url = '%scredentials/checkAccountExists?%s=%s&partnerId=%s' % (serverUrl, keyName, value, self.partnerId)
        checkKey = '%sExist' % keyName

        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        resObj = json.loads(res.content)
        # remove password from comparison since it is not returned
        self.assertEqual(resObj[checkKey], True)

# test for API endpoint /credentials/resetPwd/
# test in manualTests.py
class ResetPasswordTest(ManualTest, TestCase):
    path = "/credentials/resetPwd/"
    testMethodStr = "running ./manage.py test authentication.manualTests"

print("Running unit tests on authentication/credential web services API.........")

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
