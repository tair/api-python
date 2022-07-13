#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys, getopt
import json
import copy
from django.test import TestCase, Client
from metering.models import IpAddressCount, LimitValue
from partner.testSamples import PartnerSample
from partner.models import Partner
from common.tests import TestGenericInterfaces, GenericCRUDTest, GenericTest
from .testSamples import LimitValueSample, IpAddressCountSample, MeterBlacklistSample
from http.cookies import SimpleCookie

# Create your tests here.                                                                                                                                                                                 
django.setup()
serverUrl = TestGenericInterfaces.getHost()

# ---------------------- UNIT TEST FOR BASIC CRUD OPERATIONS -------------

# test for API endpoint /meters/
class IpAddressCountCRUD(GenericCRUDTest, TestCase):

    sample = IpAddressCountSample(serverUrl)
    partnerSample = PartnerSample(serverUrl)

    def setUp(self):
        super(IpAddressCountCRUD,self).setUp()
        Partner.objects.filter(partnerId=self.partnerSample.data['partnerId']).delete()
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.sample.partnerId=self.sample.data['partnerId']=self.sample.updateData['partnerId']=self.partnerId

# test for API endpoint /meters/limits
class LimitValueCRUD(GenericCRUDTest, TestCase):

    sample = LimitValueSample(serverUrl)
    partnerSample = PartnerSample(serverUrl)

    def setUp(self):
        super(LimitValueCRUD,self).setUp()
        Partner.objects.filter(partnerId=self.partnerSample.data['partnerId']).delete()
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.sample.partnerId=self.sample.data['partnerId']=self.sample.updateData['partnerId']=self.partnerId

# test for API endpoint /meters/meterblacklist/
class MeterBlacklistCRUD(GenericCRUDTest, TestCase):

    sample = MeterBlacklistSample(serverUrl)
    partnerSample = PartnerSample(serverUrl)

    def setUp(self):
        super(MeterBlacklistCRUD,self).setUp()
        Partner.objects.filter(partnerId=self.partnerSample.data['partnerId']).delete()
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.sample.partnerId=self.sample.data['partnerId']=self.sample.updateData['partnerId']=self.partnerId


# ----------------- END OF BASIC CRUD OPERATIONS ----------------------

# test for API endpoint /meters/ip/<ip>/increment/
class IncrementMeteringCountTest(GenericTest, TestCase):
    client = Client()

    partnerSample = PartnerSample(serverUrl)
    limitValueSample = LimitValueSample(serverUrl)
    ipAddressCountSample = IpAddressCountSample(serverUrl)

    def setUp(self):
        super(IncrementMeteringCountTest, self).setUp()
        Partner.objects.filter(partnerId=self.partnerSample.data['partnerId']).delete()
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)

        self.limitValueSample.setPartnerId(self.partnerId)
        self.limitValueId = self.limitValueSample.forcePost(self.limitValueSample.data)

        self.ipAddressCountSample.setPartnerId(self.partnerId)
        self.ipAddressCountSample.setIp(IpAddressCountSample.UNDER_LIMIT_IP)
        self.ipAddressCountSample.setCount(LimitValueSample.UNDER_LIMIT_VAL)
        self.ipAddressCountId = self.ipAddressCountSample.forcePost(self.ipAddressCountSample.data)

    def test_for_increment(self):
        currentCount = self.ipAddressCountSample.getCount()
        # cannot use reverse method since we have ip value in the middle of uri
        url = '%smeters/ip/%s/increment/?partnerId=%s' % (serverUrl, self.ipAddressCountSample.getIp(), self.partnerId)

        self.client.cookies = SimpleCookie({'apiKey':self.apiKey})
        res = self.client.post(url)

        newCount = IpAddressCount.objects.get(id=self.ipAddressCountId).count
        self.assertEqual(currentCount+1, newCount)

# test for API endpoint /meters/ip/<ip>/limit/
class CheckLimitTest(GenericTest, TestCase):
    client = Client()

    partnerSample = PartnerSample(serverUrl)

    limitValueSampleWarning = LimitValueSample(serverUrl)
    limitValueSampleExceed = LimitValueSample(serverUrl)

    successIpAddressCountSample = IpAddressCountSample(serverUrl)
    limitWarningIpAddressCountSample = IpAddressCountSample(serverUrl)
    limitBlockedIpAddressCountSample = IpAddressCountSample(serverUrl)

    meterBlacklistSample = MeterBlacklistSample(serverUrl)

    def setUp(self):
        super(CheckLimitTest, self).setUp()
        Partner.objects.filter(partnerId=self.partnerSample.data['partnerId']).delete()
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)

        self.limitValueSampleWarning.setPartnerId(self.partnerId)
        self.limitValueSampleWarning.setLimitVal(LimitValueSample.WARNING_LIMIT_VAL)
        self.limitValueSampleWarning.forcePost(self.limitValueSampleWarning.data)

        self.limitValueSampleExceed.setPartnerId(self.partnerId)
        self.limitValueSampleExceed.setLimitVal(LimitValueSample.BLOCKING_LIMIT_VAL)
        self.limitValueSampleExceed.forcePost(self.limitValueSampleExceed.data)

        self.successIpAddressCountSample.setPartnerId(self.partnerId)
        self.successIpAddressCountSample.setIp(IpAddressCountSample.UNDER_LIMIT_IP)
        self.successIpAddressCountSample.setCount(LimitValueSample.UNDER_LIMIT_VAL)
        self.successIpAddressCountSample.forcePost(self.successIpAddressCountSample.data)

        self.limitWarningIpAddressCountSample.setPartnerId(self.partnerId)
        self.limitWarningIpAddressCountSample.setIp(IpAddressCountSample.WARNING_HIT_IP)
        self.limitWarningIpAddressCountSample.setCount(LimitValueSample.WARNING_LIMIT_VAL)
        self.limitWarningIpAddressCountSample.forcePost(self.limitWarningIpAddressCountSample.data)

        self.limitBlockedIpAddressCountSample.setPartnerId(self.partnerId)
        self.limitBlockedIpAddressCountSample.setIp(IpAddressCountSample.BLOCKING_HIT_IP)
        self.limitBlockedIpAddressCountSample.setCount(LimitValueSample.BLOCKING_LIMIT_VAL)
        self.limitBlockedIpAddressCountSample.forcePost(self.limitBlockedIpAddressCountSample.data)

        self.meterBlacklistSample.setPartnerId(self.partnerId)
        self.meterBlacklistSample.setPattern(MeterBlacklistSample.BLOCKED_URI)
        self.meterBlacklistSample.forcePost(self.meterBlacklistSample.data)

    def test_for_check_limit(self):
        uri = MeterBlacklistSample.UNBLOCKED_URI
        # test for under limit
        # cannot use reverse method since we have ip value in the middle of uri
        url = '%smeters/ip/%s/limit/?partnerId=%s&uri=%s' % (serverUrl, self.successIpAddressCountSample.getIp(), self.partnerId, uri)
        self.assert_check_limit(url, 'OK')
        # test for hit limit warning
        url = '%smeters/ip/%s/limit/?partnerId=%s&uri=%s' % (serverUrl, self.limitWarningIpAddressCountSample.getIp(), self.partnerId, uri)
        self.assert_check_limit(url, 'Warning')
        # test for over limit 
        url = '%smeters/ip/%s/limit/?partnerId=%s&uri=%s' % (serverUrl, self.limitBlockedIpAddressCountSample.getIp(), self.partnerId, uri)
        self.assert_check_limit(url, 'Block')

    def assert_check_limit(self, url, status):
        self.client.cookies = SimpleCookie({'apiKey':self.apiKey})
        res = self.client.get(url)
        if res.status_code == 200:
            self.assertEqual(json.loads(res.content)['status'], status)
        else:
            self.fail('failed to run test, response code is %s' % res.status_code)

    def test_for_blacklisted_url(self):
        uri = MeterBlacklistSample.BLOCKED_URI
        url = '%smeters/ip/%s/limit/?partnerId=%s&uri=%s' % (serverUrl, self.successIpAddressCountSample.getIp(), self.partnerId, uri)
        self.assert_check_limit(url, 'BlackListBlock')

print("Running unit tests on metering web services API.........")

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)