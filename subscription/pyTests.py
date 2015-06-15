#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys, getopt
from unittest import TestCase
from subscription.models import Subscription, SubscriptionTransaction, ActivationCode
from partner.models import Partner
import requests
import json
from testSamples import SubscriptionSample, SubscriptionTransactionSample, ActivationCodeSample
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

class ActivationCodeCRUD(GenericCRUDTest, TestCase):
    sample = ActivationCodeSample(serverUrl)
    partnerSample = PartnerSample(serverUrl)

    def setUp(self):
        super(ActivationCodeCRUD, self).setUp()
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.sample.data['partnerId'] = self.sample.updateData['partnerId']=self.partnerId

        # delete activationCode entries that will be used for test
        ActivationCode.objects.filter(activationCode=self.sample.data['activationCode']).delete()
        ActivationCode.objects.filter(activationCode=self.sample.updateData['activationCode']).delete()

    def tearDown(self):
        super(ActivationCodeCRUD,self).tearDown()
        PyTestGenerics.forceDelete(self.partnerSample.model, self.partnerSample.pkName, self.partnerId)
        

class SubscriptionCRUD(GenericCRUDTest, TestCase):

    sample = SubscriptionSample(serverUrl)
    partySample = PartySample(serverUrl)
    partnerSample = PartnerSample(serverUrl)
    activationCodeSample = ActivationCodeSample(serverUrl)

    def setUp(self):
        super(SubscriptionCRUD,self).setUp()
        self.partyId = self.partySample.forcePost(self.partySample.data)
        Partner.objects.filter(partnerId=self.partnerSample.data['partnerId']).delete()
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        ActivationCode.objects.filter(activationCode=self.activationCodeSample.data['activationCode']).delete()
        self.activationCodeId = self.activationCodeSample.forcePost(self.activationCodeSample.data)
        self.sample.data['partyId']=self.sample.updateData['partyId']=self.partyId
        self.sample.partnerId=self.sample.data['partnerId']=self.sample.updateData['partnerId']=self.partnerId

    # post request for subscription is not generic. It creates a SubscriptionTransaction
    # object in addition to a Subscription object.
    def test_for_create(self):
        sample = self.sample
        url = sample.url
        cookies = {'apiKey':self.apiKey}

        # Creation via basic CRUD format
        req = requests.post(url, data=sample.data, cookies=cookies)
        self.assertEqual(req.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(PyTestGenerics.forceGet(sample.model,sample.pkName,req.json()[sample.pkName]))
        transactionId = req.json()['subscriptionTransactionId']
        self.assertIsNotNone(PyTestGenerics.forceGet(SubscriptionTransaction,'subscriptionTransactionId',transactionId))
        PyTestGenerics.forceDelete(SubscriptionTransaction, 'subscriptionTransactionId', transactionId)
        PyTestGenerics.forceDelete(sample.model,sample.pkName,req.json()[sample.pkName])

        # Creationg via activation code
        activationCode = ActivationCode.objects.get(activationCodeId=self.activationCodeId).activationCode
        data ={"partyId":self.partyId, "activationCode":activationCode}
        req = requests.post(url, data=data, cookies=cookies)
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
        PyTestGenerics.forceDelete(self.activationCodeSample.model, self.activationCodeSample.pkName, self.activationCodeId)

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

        url = serverUrl + 'subscriptions/' + str(subscriptionId) + '/renewal?apiKey=%s' % self.apiKey
        cookies = {'apiKey':self.apiKey}
        req = requests.put(url, data=subscriptionSample.updateData,cookies=cookies)
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
        url = self.url + '?partnerId=%s&partyId=%s&apiKey=%s' % (partnerId, partyId, self.apiKey)
        cookies = {'apiKey':self.apiKey}
        req = requests.get(url, cookies=cookies)
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
        url = self.url + '?partnerId=%s&ip=%s&apiKey=%s' % (partnerId, ip, self.apiKey)
        cookies = {'apiKey':self.apiKey}
        req = requests.get(url,cookies=cookies)
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

class PostPaymentHandlingTest(GenericTest, TestCase):

    partnerSample = PartnerSample(serverUrl)
    subscriptionTermSample = SubscriptionTermSample(serverUrl)

    def setUp(self):
        super(PostPaymentHandlingTest, self).setUp()
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.subscriptionTermId = self.subscriptionTermSample.forcePost(self.subscriptionTermSample.data)

    def test_for_postPaymentSubscription(self):
        activationCodeArray = PaymentControl.postPaymentHandling(self.subscriptionTermId, 5)
        for activationCode in activationCodeArray:
            self.assertIsNotNone(PyTestGenerics.forceGet(ActivationCode, 'activationCode', activationCode))
            PyTestGenerics.forceDelete(ActivationCode, 'activationCode', activationCode)

    def tearDown(self):
        super(PostPaymentHandlingTest, self).tearDown()
        PyTestGenerics.forceDelete(self.partnerSample.model, self.partnerSample.pkName, self.partnerId)
        PyTestGenerics.forceDelete(self.subscriptionTermSample.model, self.subscriptionTermSample.pkName, self.subscriptionTermId)

print "Running unit tests on subscription web services API........."

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
