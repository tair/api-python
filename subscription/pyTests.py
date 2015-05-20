#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys, getopt
from unittest import TestCase
from subscription.models import Subscription, Party, IpRange, SubscriptionTransaction
from partner.models import Partner
import requests
import json
from testSamples import SubscriptionSample, SubscriptionTransactionSample, PartySample, IpRangeSample
from partner.testSamples import PartnerSample
import copy
from common.controls import PyTestGenerics
from rest_framework import status

initPyTest = PyTestGenerics.initPyTest
genericTestCreate = PyTestGenerics.genericTestCreate
genericTestGet = PyTestGenerics.genericTestGet
genericTestGetAll = PyTestGenerics.genericTestGetAll
genericTestUpdate = PyTestGenerics.genericTestUpdate
genericTestDelete = PyTestGenerics.genericTestDelete
genericForceGet = PyTestGenerics.forceGet
genericForceDelete = PyTestGenerics.forceDelete
genericForcePost = PyTestGenerics.forcePost

# Create your tests here.                                                                                                                                                                                 
django.setup()
serverUrl = initPyTest()
print "using server url %s" % serverUrl

# ---------------------- UNIT TEST FOR BASIC CRUD OPERATIONS -------------

class SubscriptionCRUD(TestCase):

    sample = SubscriptionSample(serverUrl)
    partySample = PartySample(serverUrl)
    partnerSample = PartnerSample(serverUrl)

    def setUp(self):
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

    def test_for_getAll(self):
        genericTestGetAll(self)
 
    def test_for_update(self):
        genericTestUpdate(self)
 
    def test_for_delete(self):
        genericTestDelete(self)
 
    def test_for_get(self):
        genericTestGet(self)

    def tearDown(self):
        genericForceDelete(self.partySample.model, self.partySample.pkName, self.partyId)
        genericForceDelete(self.partnerSample.model, self.partnerSample.pkName, self.partnerId)

class SubscriptionTransactionCRUD(TestCase):
    sample = SubscriptionTransactionSample(serverUrl)

    partySample = PartySample(serverUrl)
    partnerSample = PartnerSample(serverUrl)
    subscriptionSample = SubscriptionSample(serverUrl)

    def setUp(self):
        self.partyId = self.partySample.forcePost(self.partySample.data)
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.subscriptionSample.data['partyId']=self.partyId
        self.subscriptionSample.data['partnerId']=self.partnerId
        self.subscriptionId = self.subscriptionSample.forcePost(self.subscriptionSample.data)
        self.sample.data['subscriptionId']=self.sample.updateData['subscriptionId']=self.subscriptionId

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

    def tearDown(self):
        genericForceDelete(self.partySample.model, self.partySample.pkName, self.partyId)
        genericForceDelete(self.partnerSample.model, self.partnerSample.pkName, self.partnerId)
        genericForceDelete(self.subscriptionSample.model, self.subscriptionSample.pkName, self.subscriptionId)

class PartyCRUD(TestCase):
    sample = PartySample(serverUrl)
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

class IpRangeCRUD(TestCase):
    sample = IpRangeSample(serverUrl)
    partySample = PartySample(serverUrl)

    def setUp(self):
        partyId = self.partySample.forcePost(self.partySample.data)
        self.sample.data['partyId']=self.sample.updateData['partyId']=partyId

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

    def tearDown(self):
        genericForceDelete(self.partySample.model, self.partySample.pkName, self.sample.data['partyId'])

# ----------------- END OF BASIC CRUD OPERATIONS ----------------------

class SubscriptionRenewalTest(TestCase):
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

class SubscriptionActiveTest(TestCase):
    url = serverUrl+'subscriptions/active/'
    partnerId = 'tair'
    successIp = '123.1.0.0'
    failIp = '12.2.3.4'
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
    ipRangeData = {
        'start':'123.0.0.0',
        'end':'123.255.255.255',
        'partyId':None, # To be populated after Party is created
    }
    partyData ={
        'partyType':'user',
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
        genericForceDelete(subscriptionSample.model, subscriptionSample.pkName, subscriptionId)
        genericForceDelete(partySample.model, partySample.pkName, partyId)
        genericForceDelete(partnerSample.model, partnerSample.pkName, partnerId)

    def runIpTest(self, ipRangeData, ip, shouldSuccess):
        # initialization
        partnerSample = PartnerSample(serverUrl)
        partySample = PartySample(serverUrl)
        subscriptionSample = SubscriptionSample(serverUrl)
        ipRangeSample = IpRangeSample(serverUrl)

        # setting up local data that would be modified
        lIpRangeData = copy.deepcopy(ipRangeData)
        lSubscriptionData = copy.deepcopy(subscriptionSample.data)

        # creating object
        partnerId = partnerSample.forcePost(partnerSample.data)
        partyId = partySample.forcePost(partySample.data)
        lSubscriptionData['partyId'] = partyId
        lSubscriptionData['partnerId'] = partnerId
        subscriptionId = subscriptionSample.forcePost(lSubscriptionData)
        lIpRangeData['partyId'] = partyId
        ipRangeId = ipRangeSample.forcePost(lIpRangeData)

        # run test
        url = self.url + '?partnerId=%s&ip=%s' % (partnerId, ip)
        req = requests.get(url)
        self.assertEqual(req.json()['active'], shouldSuccess)

        # delete objects
        genericForceDelete(subscriptionSample.model, subscriptionSample.pkName, subscriptionId)
        genericForceDelete(ipRangeSample.model, ipRangeSample.pkName, ipRangeId)
        genericForceDelete(partySample.model, partySample.pkName, partyId)
        genericForceDelete(partnerSample.model, partnerSample.pkName, partnerId)

    # main test for subscription active
    def test_for_SubscriptionActive(self):
        self.runIdTest(self.successSubscriptionData, True)
        self.runIdTest(self.failStartDateSubscriptionData, False)
        self.runIdTest(self.failEndDateSubscriptionData, False)
        self.runIpTest(self.ipRangeData, self.successIp, True)
        self.runIpTest(self.ipRangeData, self.failIp, False)

print "Running unit tests on subscription web services API........."

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
