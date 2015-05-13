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
import copy
from common.controls import PyTestGenerics

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

class SubscriptionTransactionCRUD(TestCase):
    sample = SubscriptionTransactionSample(serverUrl)
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

# ----------------- END OF BASIC CRUD OPERATIONS ----------------------

class SubscriptionPyTest(TestCase):
    url = serverUrl+'subscriptions/active/'
    partnerId = 'tair'
    successIp = '123.1.0.0'
    failIp = '12.2.3.4'
    successSubscriptionData = {
        'startDate':'2012-04-12T00:00:00Z',
        'endDate':'2018-04-12T00:00:00Z',
        'partnerId':'tair',
        'partyId':None, # To be populated after Party is created
    }
    failEndDateSubscriptionData = {
        'startDate':'2012-04-12T00:00:00Z',
        'endDate':'2014-04-12T00:00:00Z',
        'partnerId':'tair',
        'partyId':None, # To be populated after Party is created
    }
    failStartDateSubscriptionData = {
        'startDate':'2018-04-12T00:00:00Z',
        'endDate':'2020-04-12T00:00:00Z',
        'partnerId':'tair',
        'partyId':None, # To be populated after Party is created
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
        partySample = PartySample(serverUrl)
        subscriptionSample = SubscriptionSample(serverUrl)

        # setting up data
        subscriptionSample.data = subscriptionData

        # creating objects
        partyId = partySample.forcePost(partySample.data)
        subscriptionSample.data['partyId'] = partyId
        subscriptionId = subscriptionSample.forcePost(subscriptionSample.data)

        # run test
        url = self.url + '?partnerId=%s&partyId=%s' % (self.partnerId, partyId)
        req = requests.get(url)
        self.assertEqual(req.json()['active'], shouldSuccess)

        # delete objects
        genericForceDelete(subscriptionSample.model, subscriptionSample.pkName, subscriptionId)
        genericForceDelete(partySample.model, partySample.pkName, partyId)

    def runIpTest(self, ipRangeData, ip, shouldSuccess):
        # initialization
        partySample = PartySample(serverUrl)
        subscriptionSample = SubscriptionSample(serverUrl)
        ipRangeSample = IpRangeSample(serverUrl)

        # setting up data
        ipRangeSample.data = ipRangeData

        # creating object
        partyId = partySample.forcePost(partySample.data)
        subscriptionSample.data['partyId'] = partyId
        subscriptionId = subscriptionSample.forcePost(subscriptionSample.data)
        ipRangeSample.data['partyId'] = partyId
        ipRangeId = ipRangeSample.forcePost(ipRangeSample.data)

        # run test
        url = self.url + '?partnerId=%s&ip=%s' % (self.partnerId, ip)
        req = requests.get(url)
        self.assertEqual(req.json()['active'], shouldSuccess)

        # delete objects
        genericForceDelete(subscriptionSample.model, subscriptionSample.pkName, subscriptionId)
        genericForceDelete(ipRangeSample.model, ipRangeSample.pkName, ipRangeId)
        genericForceDelete(partySample.model, partySample.pkName, partyId)

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
