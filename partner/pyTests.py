#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  
import sys
import django
import unittest
from unittest import TestCase
from partner.models import Partner, PartnerPattern, SubscriptionTerm, SubscriptionDescription, SubscriptionDescriptionItem
import copy
from common.pyTests import PyTestGenerics, GenericCRUDTest, GenericTest
from testSamples import PartnerSample, PartnerPatternSample, SubscriptionTermSample, SubscriptionDescriptionSample, SubscriptionDescriptionItemSample
import requests

initPyTest = PyTestGenerics.initPyTest
genericForceDelete = PyTestGenerics.forceDelete

# Create your tests here.                                                                                                                                                                                 
django.setup()
serverUrl = initPyTest()

print "using server url %s" % serverUrl

class PartnerCRUD(GenericCRUDTest, TestCase):
    sample = PartnerSample(serverUrl)

    def test_for_create(self):
        Partner.objects.filter(partnerId=self.sample.data['partnerId']).delete()
        super(PartnerCRUD, self).test_for_create()

    def test_for_getByUri(self):
        partnerSample = PartnerSample(serverUrl)
        Partner.objects.filter(partnerId=partnerSample.data['partnerId']).delete()
        partnerId = partnerSample.forcePost(partnerSample.data)
        
        partnerPatternSample = PartnerPatternSample(serverUrl)
        partnerPatternSample.data['partnerId'] = partnerId
        partnerPatternId = partnerPatternSample.forcePost(partnerPatternSample.data)
        url = self.sample.url + "?uri=%s" % (partnerPatternSample.data['sourceUri'])
        cookies = {'apiKey':self.apiKey}
        req = requests.get(url,cookies=cookies)
        self.assertEqual(len(req.json()) > 0, True)
        genericForceDelete(partnerPatternSample.model, partnerPatternSample.pkName, partnerPatternId)
        genericForceDelete(partnerSample.model, partnerSample.pkName, partnerId)

class PartnerPatternCRUD(GenericCRUDTest, TestCase):
    sample = PartnerPatternSample(serverUrl)
    partnerSample = PartnerSample(serverUrl)
    def setUp(self):
        super(PartnerPatternCRUD,self).setUp()
        Partner.objects.filter(partnerId=self.partnerSample.data['partnerId']).delete()
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.sample.partnerId=self.sample.data['partnerId']=self.sample.updateData['partnerId']=self.partnerId

    def tearDown(self):
        super(PartnerPatternCRUD,self).tearDown()
        genericForceDelete(self.partnerSample.model, self.partnerSample.pkName, self.partnerId)

class SubscriptionTermCRUD(GenericCRUDTest, TestCase):
    sample = SubscriptionTermSample(serverUrl)
    partnerSample = PartnerSample(serverUrl)
    def setUp(self):
        super(SubscriptionTermCRUD,self).setUp()
        Partner.objects.filter(partnerId=self.partnerSample.data['partnerId']).delete()
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.sample.partnerId=self.sample.data['partnerId']=self.sample.updateData['partnerId']=self.partnerId
    def tearDown(self):
        super(SubscriptionTermCRUD,self).tearDown()
        genericForceDelete(self.partnerSample.model, self.partnerSample.pkName, self.partnerId)

print "Running unit tests on partner web services API........."

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
