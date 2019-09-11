#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys, getopt
import json
import copy
from django.test import TestCase, Client
from partner.testSamples import PartnerSample
from party.testSamples import UserPartySample
from common.tests import TestGenericInterfaces, GenericCRUDTest, GenericTest
from .testSamples import PageViewSample
from http.cookies import SimpleCookie

# Create your tests here.                                                                                                                                                                                 
django.setup()
serverUrl = TestGenericInterfaces.getHost()

# ---------------------- UNIT TEST FOR BASIC CRUD OPERATIONS -------------

# test for API end point /session-logs/page-views/
class PageViewCRUD(GenericCRUDTest, TestCase):
    sample = PageViewSample(serverUrl)
    partySample = UserPartySample(serverUrl)
    partnerSample = PartnerSample(serverUrl);

    def setUp(self):
        super(PageViewCRUD, self).setUp()
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.partyId = self.partySample.forcePost(self.partySample.data)
        self.sample.data['partnerId']=self.sample.updateData['partnerId']=self.partnerId
        self.sample.data['partyId']=self.sample.updateData['partyId']=self.partyId

    # update and delete are not allowed in this CRUD
    def test_for_update(self):
        pass

    def test_for_delete(self):
        pass

# ----------------- END OF BASIC CRUD OPERATIONS ----------------------

# test for API end point /session-logs/sessions/counts/
class SessionCountViewTest(GenericTest, TestCase):
    url = serverUrl + 'session-logs/sessions/counts/'

    # sessionId, pageViewDate
    sampleData = [
        (PageViewSample.SESSION_ID_I, '1980-01-01T00:35:00Z'),
        (PageViewSample.SESSION_ID_I, '1980-01-01T00:55:00Z'),
        (PageViewSample.SESSION_ID_I, '1980-01-01T00:57:00Z'),
        (PageViewSample.SESSION_ID_I, '1980-01-01T01:04:00Z'),
        (PageViewSample.SESSION_ID_II, '1981-01-01T00:00:00Z'),
        (PageViewSample.SESSION_ID_III, '1982-01-01T00:00:00Z'),
        (PageViewSample.SESSION_ID_III, '1982-01-01T00:02:00Z'),
    ]
    pageViewIdList = []
    sample = PageViewSample(serverUrl)
    partySample = UserPartySample(serverUrl)
    partnerSample = PartnerSample(serverUrl)

    def setUp(self):
        super(SessionCountViewTest, self).setUp()
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        self.partyId = self.partySample.forcePost(self.partySample.data)
        self.sample.data['partnerId']=self.partnerId
        self.sample.data['partyId']=self.partyId
        for entry in self.sampleData:
            self.sample.data['sessionId'] = entry[0]
            self.sample.data['pageViewDate'] = entry[1]
            self.pageViewIdList.append(self.sample.forcePost(self.sample.data))

    def test_for_get(self):
        self.runTest('1979-05-01T00:00:00Z', '1980-05-01T00:00:00Z', 1) #only session I
        self.runTest('1979-05-01T00:00:00Z', '1981-05-01T00:00:00Z', 2) #session I,II
        self.runTest('1979-05-01T00:00:00Z', '1982-05-01T00:00:00Z', 3) #sessionId I, II and III

    def runTest(self, startDate, endDate, expectedCount):
        url = self.url + '?apiKey=%s' % self.apiKey
        if startDate:
            url += '&startDate=%s' % startDate
        if endDate:
            url += '&endDate=%s' % endDate

        self.client.cookies = SimpleCookie({'apiKey':self.apiKey})
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        count = json.loads(res.content)['count']
        self.assertEqual(count, expectedCount)

# skipped testing for /session-logs/page-views/csv/ since no external resource uses its

print("Running unit tests on session logs web services API.........")

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
