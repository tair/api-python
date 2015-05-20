#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  
import sys
import django
import unittest
from unittest import TestCase
from partner.models import Partner, PartnerPattern, SubscriptionTerm
import copy
from common.controls import PyTestGenerics
from testSamples import PartnerSample, PartnerPatternSample, SubscriptionTermSample
import requests

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

class PartnerCRUD(TestCase):
    sample = PartnerSample(serverUrl)
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
    def test_for_getByUri(self):
        partnerPatternSample = PartnerPatternSample(serverUrl)
        partnerPatternId = partnerPatternSample.forcePost(partnerPatternSample.data)
        partnerId = self.sample.forcePost(self.sample.data)
        url = self.sample.url + "?uri=%s" % partnerPatternSample.data['pattern']
        req = requests.get(url)
        self.assertEqual(len(req.json()) > 0, True)
        genericForceDelete(partnerPatternSample.model, partnerPatternSample.pkName, partnerPatternId)
        genericForceDelete(self.sample.model, self.sample.pkName, partnerId)

class PartnerPatternCRUD(TestCase):
    sample = PartnerPatternSample(serverUrl)
    partnerSample = PartnerSample(serverUrl)
    def setUp(self):
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.sample.partnerId=self.sample.data['partnerId']=self.sample.updateData['partnerId']=self.partnerId
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
        genericForceDelete(self.partnerSample.model, self.partnerSample.pkName, self.partnerId)

class SubscriptionTermCRUD(TestCase):
    sample = SubscriptionTermSample(serverUrl)
    partnerSample = PartnerSample(serverUrl)
    def setUp(self):
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.sample.partnerId=self.sample.data['partnerId']=self.sample.updateData['partnerId']=self.partnerId
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
        genericForceDelete(self.partnerSample.model, self.partnerSample.pkName, self.partnerId)

class SubscriptionTermQueryTest(TestCase):
    url = serverUrl+'partners/terms/queries/'

    def runSubscriptionTermQueryTest(self, key, value, shouldSuccess):
        #initialization
        subscriptionTermSample = SubscriptionTermSample(serverUrl)
        partnerSample = PartnerSample(serverUrl)

        #setup data
        pass

        #creating objects
        partnerId = partnerSample.forcePost(partnerSample.data)
        subscriptionTermSample.data['partnerId']=partnerId
        subscriptionTermId = subscriptionTermSample.forcePost(subscriptionTermSample.data)

        #run tests
        url = self.url + '?partnerId=%s&%s=%s' % (partnerId, key, value)
        req = requests.get(url)
        self.assertEqual(len(req.json()) > 0, shouldSuccess)

        #delete objects
        genericForceDelete(subscriptionTermSample.model, subscriptionTermSample.pkName, subscriptionTermId)
        genericForceDelete(partnerSample.model, partnerSample.pkName, partnerId)

    def test_for_subscriptionTermQuery(self):
        sample = SubscriptionTermSample(serverUrl)
        self.runSubscriptionTermQueryTest('price', sample.data['price'], True)
        self.runSubscriptionTermQueryTest('price', sample.data['price']+5, False)
        self.runSubscriptionTermQueryTest('period', sample.data['period'], True)
        self.runSubscriptionTermQueryTest('period', sample.data['period']+5, False)

print "Running unit tests on partner web services API........."

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
