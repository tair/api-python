#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys, getopt
import requests
from unittest import TestCase
from common.controls import PyTestGenerics, GenericCRUDTest, GenericTest

from subscription.pyTests import SubscriptionActiveTest
from subscription.testSamples import SubscriptionSample
from party.testSamples import IpRangeSample, PartySample
from partner.testSamples import PartnerSample
from authorization.models import Status

from testSamples import UriPatternSample, AccessRuleSample, AccessTypeSample, UsernamePartyAffiliationSample

from authentication.views import generateSecretKey

# Create your tests here.                                                                                                                                                                                 
django.setup()
serverUrl = PyTestGenerics.initPyTest()
print "using server url %s" % serverUrl


# ---------------------- UNIT TEST FOR BASIC CRUD OPERATIONS -------------

class UriPatternCRUD(GenericCRUDTest, TestCase):
    sample = UriPatternSample(serverUrl)

class AccessRuleCRUD(GenericCRUDTest, TestCase):
    sample = AccessRuleSample(serverUrl)
    partnerSample = PartnerSample(serverUrl)
    patternSample = UriPatternSample(serverUrl)
    accessTypeSample = AccessTypeSample(serverUrl)
    def setUp(self):
        super(AccessRuleCRUD,self).setUp()
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.patternId = self.patternSample.forcePost(self.patternSample.data)
        self.accessTypeId = self.accessTypeSample.forcePost(self.accessTypeSample.data)
        self.sample.partnerId=self.sample.data['partnerId']=self.sample.updateData['partnerId']=self.partnerId
        self.sample.data['patternId']=self.sample.updateData['patternId']=self.patternId
        self.sample.data['accessTypeId']=self.sample.data['accessTypeId']=self.accessTypeId

    def tearDown(self):
        super(AccessRuleCRUD,self).tearDown()
        PyTestGenerics.forceDelete(self.partnerSample.model, self.partnerSample.pkName, self.partnerId)
        PyTestGenerics.forceDelete(self.patternSample.model, self.patternSample.pkName, self.patternId)
        PyTestGenerics.forceDelete(self.accessTypeSample.model, self.accessTypeSample.pkName, self.accessTypeId)

class AccessTypesCRUD(GenericCRUDTest, TestCase):
    sample = AccessTypeSample(serverUrl)

# ----------------- END OF BASIC CRUD OPERATIONS ----------------------


# Base class for sample management for access, subscription, and authorization access tests.
class AuthorizationTestBase(GenericTest, TestCase):
    successIp = SubscriptionActiveTest.successIp
    failIp = SubscriptionActiveTest.failIp

    successSubscriptionData = SubscriptionActiveTest.successSubscriptionData
    failSubscriptionData = SubscriptionActiveTest.failEndDateSubscriptionData

    def initSamples(self):
        self.partnerSample = PartnerSample(serverUrl)
        self.partySample = PartySample(serverUrl)
        self.subscriptionSample = SubscriptionSample(serverUrl)
        self.ipRangeSample = IpRangeSample(serverUrl)
        self.uriPatternSample = UriPatternSample(serverUrl)
        self.accessTypeSample = AccessTypeSample(serverUrl)
        self.accessRuleSample = AccessRuleSample(serverUrl)
        self.usernamePartyAffiliationSample = UsernamePartyAffiliationSample()

    def createSamples(self):
        # create independent objects
        self.accessTypeId = self.accessTypeSample.forcePost(self.accessTypeSample.data)
        self.uriPatternId = self.uriPatternSample.forcePost(self.uriPatternSample.data)
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.partyId = self.partySample.forcePost(self.partySample.data)
        
        # create AccessRule based on AccessType, Pattern, and Partner objects created
        self.accessRuleSample.data['accessTypeId']=self.accessTypeId
        self.accessRuleSample.data['patternId']=self.uriPatternId
        self.accessRuleSample.data['partnerId'] = self.partnerId
        self.accessRuleId = self.accessRuleSample.forcePost(self.accessRuleSample.data)

        # create Subscription object based on Party and Partner objects created
        self.subscriptionSample.data['partyId'] = self.partyId
        self.subscriptionSample.data['partnerId'] = self.partnerId
        self.subscriptionId = self.subscriptionSample.forcePost(self.subscriptionSample.data)
        
        # create IpRange object based on data Party created
        self.ipRangeSample.data['partyId'] = self.partyId
        self.ipRangeId = self.ipRangeSample.forcePost(self.ipRangeSample.data)

        # create UsernamePartyAffiliation object based on Party created
        PyTestGenerics.forceDelete(self.usernamePartyAffiliationSample.model, 'username', self.usernamePartyAffiliationSample.data['username'])
        self.usernamePartyAffiliationSample.data['partyId'] = self.partyId
        self.usernamePartyAffiliationId = self.usernamePartyAffiliationSample.forcePost(self.usernamePartyAffiliationSample.data)

    def deleteSamples(self):
        PyTestGenerics.forceDelete(self.subscriptionSample.model, self.subscriptionSample.pkName, self.subscriptionId)
        PyTestGenerics.forceDelete(self.ipRangeSample.model, self.ipRangeSample.pkName, self.ipRangeId)
        PyTestGenerics.forceDelete(self.partySample.model, self.partySample.pkName, self.partyId)
        PyTestGenerics.forceDelete(self.partnerSample.model, self.partnerSample.pkName, self.partnerId)
        PyTestGenerics.forceDelete(self.accessTypeSample.model, self.accessTypeSample.pkName, self.accessTypeId)
        PyTestGenerics.forceDelete(self.uriPatternSample.model, self.uriPatternSample.pkName, self.uriPatternId)
        PyTestGenerics.forceDelete(self.accessRuleSample.model, self.accessRuleSample.pkName, self.accessRuleId)
        PyTestGenerics.forceDelete(self.usernamePartyAffiliationSample.model, self.usernamePartyAffiliationSample.pkName, self.usernamePartyAffiliationId)

class AuthenticationTest(AuthorizationTestBase):
    url = serverUrl+'authorizations/authentications/'

    def runTest(self, urlType, expectedStatus):
        #initialize samples
        self.initSamples()

        # setting up data
        self.accessTypeSample.data['name'] = urlType

        # create sample models in database
        self.createSamples()

        # run the system test
        loginKey = generateSecretKey(self.partyId, self.usernamePartyAffiliationSample.data['password'])
        url = self.url + '?partnerId=%s&url=%s&partyId=%s' % (self.partnerId, self.uriPatternSample.data['pattern'], self.partyId)
        cookies = {'loginKey':loginKey}
        req = requests.get(url,cookies=cookies)
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json()['access'], expectedStatus)

        # delete samples in database
        self.deleteSamples()

    def test_for_authentication(self):
        self.runTest("Login", True)

class SubscriptionTest(AuthorizationTestBase):
    url = serverUrl+'authorizations/subscriptions/'

    def runTest(self, subscriptionData, usePartyId, ip, urlType, expectedStatus):
        #initialize samples
        self.initSamples()
        
        # setting up data
        self.subscriptionSample.data = subscriptionData
        self.accessTypeSample.data['name'] = urlType

        # create sample models in database
        self.createSamples()
        
        # run the system test
        url = self.url + '?partnerId=%s&url=%s' % (self.partnerId, self.uriPatternSample.data['pattern'])
        if not ip == None:
            url = url+'&ip=%s' % (ip)
        if usePartyId:
            url = url+'&partyId=%s' % (self.partyId)

        req = requests.get(url)
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json()['access'], expectedStatus)

        # delete samples in database
        self.deleteSamples()

    def test_for_subscription(self):
        # valid subscription based on partyId, Paid url. access should be True
        self.runTest(self.successSubscriptionData, True, None, 'Paid', True)
        # invalid subscription, Paid url. access should be False
        self.runTest(self.failSubscriptionData, True, None, 'Paid', False)
        # invalid subscription, not Paid url. access should be True
        self.runTest(self.failSubscriptionData, True, None, 'Free', True)
        # valid subscription based on IP, Paid url, access should be True
        self.runTest(self.successSubscriptionData, False, self.successIp, 'Paid', True) 

class AccessTest(AuthorizationTestBase):
    url = serverUrl+'authorizations/access/'

    def runTest(self, subscriptionData, usePartyId, ip, urlType, expectedStatus):
        # initialize samples
        self.initSamples()

        # setting up data
        self.subscriptionSample.data = subscriptionData
        self.accessTypeSample.data['name'] = urlType

        # create sample models in database
        self.createSamples()

        # run the system test
        url = self.url + '?partnerId=%s&url=%s' % (self.partnerId, self.uriPatternSample.data['pattern'])
        if not ip == None:
            url = url+'&ip=%s' % (ip)
        if usePartyId:
            url = url+'&partyId=%s' % (self.partyId)
        req = requests.get(url)
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json()['status'], expectedStatus)

        # delete samples in database
        self.deleteSamples()

    def test_for_access(self):
        # valid subscription, paid url, status should be OK
        self.runTest(self.successSubscriptionData, True, None, 'Paid', Status.ok)
        # invalid subscription, paid url, status should be need subscription
        self.runTest(self.failSubscriptionData, True, None, 'Paid', Status.needSubscription)
        #self.runAccessTest(self.successSubscriptionData, False, self.successIp, self.paidUrl, Status.ok)

print "Running unit tests on authorization web services API........."

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
