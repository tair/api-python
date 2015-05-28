#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys, getopt
from unittest import TestCase
from subscription.models import Subscription, SubscriptionTransaction
from partner.models import Partner
import requests
import json
from testSamples import SubscriptionSample, SubscriptionTransactionSample
from party.testSamples import PartySample, IpRangeSample
from partner.testSamples import PartnerSample, SubscriptionTermSample
import copy
from common.pyTests import PyTestGenerics, GenericCRUDTest, GenericTest
from rest_framework import status
from controls import PaymentControl

# Create your tests here.                                                                                                                                                                                 
django.setup()
serverUrl = PyTestGenerics.initPyTest()
print "using server url %s" % serverUrl

# ---------------------- UNIT TEST FOR BASIC CRUD OPERATIONS -------------

class SubscriptionCRUD(GenericCRUDTest, TestCase):

    sample = SubscriptionSample(serverUrl)
    partySample = PartySample(serverUrl)
    partnerSample = PartnerSample(serverUrl)

    def setUp(self):
        super(SubscriptionCRUD,self).setUp()
        self.partyId = self.partySample.forcePost(self.partySample.data)
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.sample.data['partyId']=self.sample.updateData['partyId']=self.partyId
        self.sample.partnerId=self.sample.data['partnerId']=self.sample.updateData['partyId']=self.partnerId

    # post request for subscription is not generic. It creates a SubscriptionTransaction
    # object in addition to a Subscription object.
    def test_for_create(self):
        sample = self.sample
        req = requests.post(sample.url, data=sample.data)
        self.assertEqual(req.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(PyTestGenerics.forceGet(sample.model,sample.pkName,req.json()[sample.pkName]))
        transactionId = req.json()['subscriptionTransactionId']
        self.assertIsNotNone(PyTestGenerics.forceGet(SubscriptionTransaction,'subscriptionTransactionId',transactionId))
        PyTestGenerics.forceDelete(SubscriptionTransaction, 'subscriptionTransactionId', transactionId)
        PyTestGenerics.forceDelete(sample.model,sample.pkName,req.json()[sample.pkName])

    def tearDown(self):
        super(SubscriptionCRUD,self).tearDown()
        PyTestGenerics.forceDelete(self.partySample.model, self.partySample.pkName, self.partyId)
        PyTestGenerics.forceDelete(self.partnerSample.model, self.partnerSample.pkName, self.partnerId)

class SubscriptionTransactionCRUD(GenericCRUDTest, TestCase):
    sample = SubscriptionTransactionSample(serverUrl)

    partySample = PartySample(serverUrl)
    partnerSample = PartnerSample(serverUrl)
    subscriptionSample = SubscriptionSample(serverUrl)

    def setUp(self):
        super(SubscriptionTransactionCRUD,self).setUp()
        self.partyId = self.partySample.forcePost(self.partySample.data)
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.subscriptionSample.data['partyId']=self.partyId
        self.subscriptionSample.data['partnerId']=self.partnerId
        self.subscriptionId = self.subscriptionSample.forcePost(self.subscriptionSample.data)
        self.sample.data['subscriptionId']=self.sample.updateData['subscriptionId']=self.subscriptionId

    def tearDown(self):
        super(SubscriptionTransactionCRUD,self).tearDown()
        PyTestGenerics.forceDelete(self.partySample.model, self.partySample.pkName, self.partyId)
        PyTestGenerics.forceDelete(self.partnerSample.model, self.partnerSample.pkName, self.partnerId)
        PyTestGenerics.forceDelete(self.subscriptionSample.model, self.subscriptionSample.pkName, self.subscriptionId)

# ----------------- END OF BASIC CRUD OPERATIONS ----------------------

class SubscriptionRenewalTest(GenericTest, TestCase):
    def test_for_update(self):
        subscriptionSample = SubscriptionSample(serverUrl)
        partnerSample = PartnerSample(serverUrl)
        partySample = PartySample(serverUrl)

        partnerId = partnerSample.forcePost(partnerSample.data)
        partyId = partySample.forcePost(partySample.data)
        
        subscriptionSample.data['partnerId']=subscriptionSample.updateData['partnerId']=partnerId
        subscriptionSample.data['partyId']=subscriptionSample.updateData['partyId']=partyId
        subscriptionId = subscriptionSample.forcePost(subscriptionSample.data)

        url = serverUrl + 'subscriptions/' + str(subscriptionId) + '/renewal'
        req = requests.put(url, data=subscriptionSample.updateData)
        self.assertEqual(req.status_code, 200)
        transactionId = req.json()['subscriptionTransactionId']
        self.assertIsNotNone(PyTestGenerics.forceGet(SubscriptionTransaction,'subscriptionTransactionId',transactionId))
        PyTestGenerics.forceDelete(SubscriptionTransaction, 'subscriptionTransactionId', transactionId)
        PyTestGenerics.forceDelete(subscriptionSample.model,subscriptionSample.pkName,subscriptionId)
        PyTestGenerics.forceDelete(partnerSample.model,partnerSample.pkName,partnerId)
        PyTestGenerics.forceDelete(partySample.model,partySample.pkName,partyId)

class SubscriptionActiveTest(GenericTest, TestCase):
    url = serverUrl+'subscriptions/active/'

    # should be consistent with IpRangeSample object
    successIp = '120.1.0.0'
    failIp = '12.2.3.4'
    
    # should be consistent with SubscriptionSample object
    successSubscriptionData = {
        'startDate':'2012-04-12T00:00:00Z',
        'endDate':'2018-04-12T00:00:00Z',
        'partnerId':None, # To be populated after Partner is created
        'partyId':None, # To be populated after Party is created
    }
    failEndDateSubscriptionData = {
        'startDate':'2012-04-12T00:00:00Z',
        'endDate':'2014-04-12T00:00:00Z',
        'partnerId':None,
        'partyId':None, 
    }
    failStartDateSubscriptionData = {
        'startDate':'2018-04-12T00:00:00Z',
        'endDate':'2020-04-12T00:00:00Z',
        'partnerId':None,
        'partyId':None,
    }

    def runIdTest(self, subscriptionData, shouldSuccess):

        #initialization
        partnerSample = PartnerSample(serverUrl)
        partySample = PartySample(serverUrl)
        subscriptionSample = SubscriptionSample(serverUrl)

        # setting up local data that would be modified
        lSubscriptionData = copy.deepcopy(subscriptionData)

        # creating objects
        partnerId = partnerSample.forcePost(partnerSample.data)
        partyId = partySample.forcePost(partySample.data)
        lSubscriptionData['partyId'] = partyId
        lSubscriptionData['partnerId'] = partnerId
        subscriptionId = subscriptionSample.forcePost(lSubscriptionData)

        # run test
        url = self.url + '?partnerId=%s&partyId=%s' % (partnerId, partyId)
        req = requests.get(url)
        print url
        self.assertEqual(req.json()['active'], shouldSuccess)

        # delete objects
        PyTestGenerics.forceDelete(subscriptionSample.model, subscriptionSample.pkName, subscriptionId)
        PyTestGenerics.forceDelete(partySample.model, partySample.pkName, partyId)
        PyTestGenerics.forceDelete(partnerSample.model, partnerSample.pkName, partnerId)

    def runIpTest(self, ip, shouldSuccess):
        # initialization
        partnerSample = PartnerSample(serverUrl)
        partySample = PartySample(serverUrl)
        subscriptionSample = SubscriptionSample(serverUrl)
        ipRangeSample = IpRangeSample(serverUrl)

        # setting up local data that would be modified
        lSubscriptionData = copy.deepcopy(subscriptionSample.data)

        # creating object
        partnerId = partnerSample.forcePost(partnerSample.data)
        partyId = partySample.forcePost(partySample.data)
        lSubscriptionData['partyId'] = partyId
        lSubscriptionData['partnerId'] = partnerId
        subscriptionId = subscriptionSample.forcePost(lSubscriptionData)
        ipRangeSample.data['partyId'] = partyId
        ipRangeId = ipRangeSample.forcePost(ipRangeSample.data)

        # run test
        url = self.url + '?partnerId=%s&ip=%s' % (partnerId, ip)
        req = requests.get(url)
        self.assertEqual(req.json()['active'], shouldSuccess)

        # delete objects
        PyTestGenerics.forceDelete(subscriptionSample.model, subscriptionSample.pkName, subscriptionId)
        PyTestGenerics.forceDelete(ipRangeSample.model, ipRangeSample.pkName, ipRangeId)
        PyTestGenerics.forceDelete(partySample.model, partySample.pkName, partyId)
        PyTestGenerics.forceDelete(partnerSample.model, partnerSample.pkName, partnerId)

    # main test for subscription active
    def test_for_SubscriptionActive(self):
        self.runIdTest(self.successSubscriptionData, True)
        self.runIdTest(self.failStartDateSubscriptionData, False)
        self.runIdTest(self.failEndDateSubscriptionData, False)
        self.runIpTest(self.successIp, True)
        self.runIpTest(self.failIp, False)

class PostPaymentSubscriptionTest(GenericTest, TestCase):

    partySample = PartySample(serverUrl)
    partnerSample = PartnerSample(serverUrl)
    subscriptionTermSample = SubscriptionTermSample(serverUrl)

    def setUp(self):
        super(PostPaymentSubscriptionTest, self).setUp()
        self.partyId = self.partySample.forcePost(self.partySample.data)
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.subscriptionTermSample.data['partnerId']=self.partnerId
        self.subscriptionTermId = self.subscriptionTermSample.forcePost(self.subscriptionTermSample.data)

    def test_for_postPaymentSubscription(self):
        (subscriptionId, subscriptionTransactionId) = PaymentControl.postPaymentSubscription(self.subscriptionTermId, self.partyId)
        self.assertIsNotNone(PyTestGenerics.forceGet(Subscription, 'subscriptionId', subscriptionId))
        self.assertIsNotNone(PyTestGenerics.forceGet(SubscriptionTransaction, 'subscriptionTransactionId', subscriptionTransactionId))

        PyTestGenerics.forceDelete(Subscription, 'subscriptionId', subscriptionId)
        PyTestGenerics.forceDelete(SubscriptionTransaction, 'subscriptionTransactionId', subscriptionTransactionId)

    def tearDown(self):
        super(PostPaymentSubscriptionTest, self).tearDown()
        PyTestGenerics.forceDelete(self.partySample.model, self.partySample.pkName, self.partyId)
        PyTestGenerics.forceDelete(self.partnerSample.model, self.partnerSample.pkName, self.partnerId)
        PyTestGenerics.forceDelete(self.subscriptionTermSample.model, self.subscriptionTermSample.pkName, self.subscriptionTermId)

print "Running unit tests on subscription web services API........."

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
