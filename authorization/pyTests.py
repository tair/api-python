#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys, getopt
import requests
from unittest import TestCase
from common.controls import PyTestGenerics

from subscription.pyTests import SubscriptionActiveTest
from subscription.testSamples import SubscriptionSample, IpRangeSample, PartySample
from authorization.models import Status

from testSamples import UriPatternSample, AccessRuleSample, AccessTypeSample

initPyTest = PyTestGenerics.initPyTest
genericTestCreate = PyTestGenerics.genericTestCreate
genericTestGet = PyTestGenerics.genericTestGet
genericTestGetAll = PyTestGenerics.genericTestGetAll
genericTestUpdate = PyTestGenerics.genericTestUpdate
genericTestDelete = PyTestGenerics.genericTestDelete
genericForceDelete = PyTestGenerics.forceDelete

# Create your tests here.                                                                                                                                                                                 
django.setup()
serverUrl = initPyTest()
print "using server url %s" % serverUrl


class UriPatternCRUD(TestCase):
    sample = UriPatternSample(serverUrl)
    def test_for_create(self):
        genericTestCreate(self)    

    def test_for_getAll(self):
        genericTestGetAll(self)
 
    def test_for_update(self):
        genericTestUpdate(self)
 
    def test_for_delete(self):
        genericTestDelete(self)
 
    def test_for_get(self):
        genericTestGet(self)

class AccessRulesCRUD(TestCase):
    sample = AccessRuleSample(serverUrl)
    def test_for_create(self):
        genericTestCreate(self)

    def test_for_getAll(self):
        genericTestGetAll(self)

    def test_for_update(self):
        genericTestUpdate(self)

    def test_for_delete(self):
        genericTestDelete(self)

    def test_for_get(self):
        genericTestGet(self)

class AccessTypesCRUD(TestCase):
    sample = AccessTypeSample(serverUrl)
    def test_for_create(self):
        genericTestCreate(self)

    def test_for_getAll(self):
        genericTestGetAll(self)

    def test_for_update(self):
        genericTestUpdate(self)

    def test_for_delete(self):
        genericTestDelete(self)

    def test_for_get(self):
        genericTestGet(self)


class AuthorizationPyTest(TestCase):
    accessUrl = serverUrl+'authorizations/access/'
    subscriptionAccessUrl = serverUrl+'authorizations/subscriptions/'

    partnerId = 'tair'
    freeUrl = '/free/'
    paidUrl = '/test/'

    successIp = SubscriptionActiveTest.successIp
    failIp = SubscriptionActiveTest.failIp

    partyData = SubscriptionActiveTest.partyData
    ipRangeData = SubscriptionActiveTest.ipRangeData
    successSubscriptionData = SubscriptionActiveTest.successSubscriptionData
    failSubscriptionData = SubscriptionActiveTest.failEndDateSubscriptionData

    subscriptionSample = SubscriptionSample(serverUrl)
    ipRangeSample = IpRangeSample(serverUrl)
    partySample = PartySample(serverUrl)

    def runAccessTest(self, subscriptionData, ipRangeData, partyData, usePartyId, ip, pattern, expectedStatus):
        # initialization
        partySample = self.partySample
        subscriptionSample = self.subscriptionSample
        ipRangeSample = self.ipRangeSample

        # setting up data
        partySample.data = partyData
        subscriptionSample.data = subscriptionData
        ipRangeSample.data = ipRangeData

        # creating object
        partyId = partySample.forcePost(partySample.data)
        subscriptionSample.data['partyId'] = partyId
        subscriptionId = subscriptionSample.forcePost(subscriptionSample.data)
        ipRangeSample.data['partyId'] = partyId
        ipRangeId = ipRangeSample.forcePost(ipRangeSample.data)

        # run test
        url = self.accessUrl + '?partnerId=%s&url=%s' % (self.partnerId, pattern)
        if not ip == None:
            url = url+'&ip=%s' % (ip)
        if usePartyId:
            url = url+'&partyId=%s' % (partyId)
        req = requests.get(url)
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json()['status'], expectedStatus)

        # delete objects
        genericForceDelete(subscriptionSample.model, subscriptionSample.pkName, subscriptionId)
        genericForceDelete(ipRangeSample.model, ipRangeSample.pkName, ipRangeId)
        genericForceDelete(partySample.model, partySample.pkName, partyId)

    def test_for_access(self):
        self.runAccessTest(self.successSubscriptionData, self.ipRangeData, self.partyData, True, None, self.paidUrl, Status.ok)
        self.runAccessTest(self.failSubscriptionData, self.ipRangeData, self.partyData, True, None, self.paidUrl, Status.needSubscription)
        self.runAccessTest(self.successSubscriptionData, self.ipRangeData, self.partyData, False, self.successIp, self.paidUrl, Status.ok)

print "Running unit tests on authorization web services API........."

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
