#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys, getopt
from unittest import TestCase
from metering.models import IpAddressCount, LimitValue
from partner.models import Partner
import requests
import json
from testSamples import LimitValueSample, IpAddressCountSample
from partner.testSamples import PartnerSample
import copy
from common.pyTests import PyTestGenerics, GenericCRUDTest, GenericTest
from rest_framework import status


# Create your tests here.                                                                                                                                                                                 
django.setup()
serverUrl = PyTestGenerics.initPyTest()
print "using server url %s" % serverUrl

# ---------------------- UNIT TEST FOR BASIC CRUD OPERATIONS -------------

class IpAddressCountCRUD(GenericCRUDTest, TestCase):

    sample = IpAddressCountSample(serverUrl)
    partnerSample = PartnerSample(serverUrl)

    def setUp(self):
        super(IpAddressCountCRUD,self).setUp()
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.sample.partnerId=self.sample.data['partnerId']=self.sample.updateData['partnerId']=self.partnerId

    def tearDown(self):
        super(IpAddressCountCRUD,self).tearDown()
        PyTestGenerics.forceDelete(self.partnerSample.model, self.partnerSample.pkName, self.partnerId)

class LimitValueCRUD(GenericCRUDTest, TestCase):

    sample = LimitValueSample(serverUrl)
    partnerSample = PartnerSample(serverUrl)

    def setUp(self):
        super(LimitValueCRUD,self).setUp()
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.sample.partnerId=self.sample.data['partnerId']=self.sample.updateData['partnerId']=self.partnerId

    def tearDown(self):
        super(LimitValueCRUD,self).tearDown()
        PyTestGenerics.forceDelete(self.partnerSample.model, self.partnerSample.pkName, self.partnerId)

# ----------------- END OF BASIC CRUD OPERATIONS ----------------------

class IncrementMeteringCountTest(GenericTest, TestCase):
    ipAddressCountSample = IpAddressCountSample(serverUrl)
    limitValueSample = LimitValueSample(serverUrl)
    partnerSample = PartnerSample(serverUrl)
    def setUp(self):
        super(IncrementMeteringCountTest, self).setUp()
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.ipAddressCountSample.data['partnerId'] = self.partnerId
        self.ipAddressCountSample.data['count'] = 1
        self.ipAddressCountId = self.ipAddressCountSample.forcePost(self.ipAddressCountSample.data)
        self.limitValueSample.data['partnerId'] = self.partnerId
        self.limitValueId = self.limitValueSample.forcePost(self.limitValueSample.data)

    def test_for_increment(self):
        currentCount = self.ipAddressCountSample.data['count']
        url = '%smeters/ip/%s/increment/?apiKey=%s' % (serverUrl, self.ipAddressCountSample.data['ip'], self.apiKey)
        cookies = {'apiKey':self.apiKey}
        req = requests.post(url, cookies=cookies)
        newCount = IpAddressCount.objects.get(id=self.ipAddressCountId).count
        self.assertEqual(currentCount+1, newCount)

    def tearDown(self):
        super(IncrementMeteringCountTest,self).tearDown()
        PyTestGenerics.forceDelete(self.partnerSample.model, self.partnerSample.pkName, self.partnerId)
        PyTestGenerics.forceDelete(self.ipAddressCountSample.model, self.ipAddressCountSample.pkName, self.ipAddressCountId)
        PyTestGenerics.forceDelete(self.limitValueSample.model, self.limitValueSample.pkName, self.limitValueId)

class CheckLimitTest(GenericTest, TestCase):
    successIpAddressCountSample = IpAddressCountSample(serverUrl)
    failIpAddressCountSample = IpAddressCountSample(serverUrl)
    limitValueSample = LimitValueSample(serverUrl)
    partnerSample = PartnerSample(serverUrl)
    successIp = '123.45.6.7'
    failIp = '123.45.6.8'
    
    def setUp(self):
        super(CheckLimitTest, self).setUp()
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.successIpAddressCountSample.data['partnerId'] = self.partnerId
        self.successIpAddressCountSample.data['count'] = 1
        self.successIpAddressCountSample.data['ip'] = self.successIp
        self.successIpAddressCountId = self.successIpAddressCountSample.forcePost(self.successIpAddressCountSample.data)
        self.failIpAddressCountSample.data['partnerId'] = self.partnerId
        self.failIpAddressCountSample.data['ip'] = self.failIp
        self.failIpAddressCountSample.data['count'] = 10000
        self.failIpAddressCountId = self.failIpAddressCountSample.forcePost(self.failIpAddressCountSample.data)
        self.limitValueSample.data['partnerId'] = self.partnerId
        self.limitValueId = self.limitValueSample.forcePost(self.limitValueSample.data)

    def test_for_check_limit(self):
        url = '%smeters/ip/%s/limit/?apiKey=%s' % (serverUrl, self.successIp, self.apiKey)
        cookies = {'apiKey':self.apiKey}
        req = requests.get(url, cookies=cookies)
        self.assertEqual(req.json()['status'], 'OK')
        url = '%smeters/ip/%s/limit/?apiKey=%s' % (serverUrl, self.failIp, self.apiKey)
        req = requests.get(url, cookies=cookies)
        self.assertEqual(req.json()['status'], 'Block')

    def tearDown(self):
        super(CheckLimitTest,self).tearDown()
        PyTestGenerics.forceDelete(self.partnerSample.model, self.partnerSample.pkName, self.partnerId)
        PyTestGenerics.forceDelete(self.successIpAddressCountSample.model, self.successIpAddressCountSample.pkName, self.successIpAddressCountId)
        PyTestGenerics.forceDelete(self.failIpAddressCountSample.model, self.failIpAddressCountSample.pkName, self.failIpAddressCountId)
        PyTestGenerics.forceDelete(self.limitValueSample.model, self.limitValueSample.pkName, self.limitValueId)

print "Running unit tests on subscription web services API........."

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
