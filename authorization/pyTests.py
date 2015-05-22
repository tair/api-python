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

from testSamples import UriPatternSample, AccessRuleSample, AccessTypeSample


# Create your tests here.                                                                                                                                                                                 
django.setup()
serverUrl = PyTestGenerics.initPyTest()
print "using server url %s" % serverUrl


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

class AuthorizationPyTest(GenericTest, TestCase):
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
    partnerSample = PartnerSample(serverUrl)

    def runAccessTest(self, subscriptionData, ipRangeData, partyData, usePartyId, ip, pattern, expectedStatus):
        # initialization
        partnerSample = self.partnerSample
        partySample = self.partySample
        subscriptionSample = self.subscriptionSample
        ipRangeSample = self.ipRangeSample
        uriPatternSample = UriPatternSample(serverUrl)
        accessTypeSample = AccessTypeSample(serverUrl)
        accessRuleSample = AccessRuleSample(serverUrl)

        # setting up data
        partySample.data = partyData
        subscriptionSample.data = subscriptionData
        ipRangeSample.data = ipRangeData
        accessTypeSample.data['name'] = 'Paid'
        uriPatternSample.data['pattern'] = pattern

        # creating object
        accessTypeId = accessTypeSample.forcePost(accessTypeSample.data)
        uriPatternId = uriPatternSample.forcePost(uriPatternSample.data)
        partnerId = partnerSample.forcePost(partnerSample.data)
        accessRuleSample.data['accessTypeId']=accessTypeId
        accessRuleSample.data['patternId']=uriPatternId
        accessRuleSample.data['partnerId'] = partnerId
        accessRuleId = accessRuleSample.forcePost(accessRuleSample.data)
        partyId = partySample.forcePost(partySample.data)
        subscriptionSample.data['partyId'] = partyId
        subscriptionSample.data['partnerId'] = partnerId
        subscriptionId = subscriptionSample.forcePost(subscriptionSample.data)
        ipRangeSample.data['partyId'] = partyId
        ipRangeId = ipRangeSample.forcePost(ipRangeSample.data)

        # run test
        url = self.accessUrl + '?partnerId=%s&url=%s' % (partnerId, pattern)
        if not ip == None:
            url = url+'&ip=%s' % (ip)
        if usePartyId:
            url = url+'&partyId=%s' % (partyId)
        req = requests.get(url)
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json()['status'], expectedStatus)

        # delete objects
        PyTestGenerics.forceDelete(subscriptionSample.model, subscriptionSample.pkName, subscriptionId)
        PyTestGenerics.forceDelete(ipRangeSample.model, ipRangeSample.pkName, ipRangeId)
        PyTestGenerics.forceDelete(partySample.model, partySample.pkName, partyId)
        PyTestGenerics.forceDelete(partnerSample.model, partnerSample.pkName, partnerId)
        PyTestGenerics.forceDelete(accessTypeSample.model, accessTypeSample.pkName, accessTypeId)
        PyTestGenerics.forceDelete(uriPatternSample.model, uriPatternSample.pkName, uriPatternId)
        PyTestGenerics.forceDelete(accessRuleSample.model, accessRuleSample.pkName, accessRuleId)

    def test_for_access(self):
        self.runAccessTest(self.successSubscriptionData, self.ipRangeData, self.partyData, True, None, self.paidUrl, Status.ok)
        self.runAccessTest(self.failSubscriptionData, self.ipRangeData, self.partyData, True, None, self.paidUrl, Status.needSubscription)
        # TODO this test requires a construction of a metering object. Defer it after metering is finalized.
        #self.runAccessTest(self.successSubscriptionData, self.ipRangeData, self.partyData, False, self.successIp, self.paidUrl, Status.ok)

print "Running unit tests on authorization web services API........."

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
