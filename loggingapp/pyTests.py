#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys, getopt
from unittest import TestCase
from party.models import Party
from partner.models import Partner
from loggingapp.models import PageView

from loggingapp.testSamples import PageViewSample
from party.testSamples import PartySample
from partner.testSamples import PartnerSample
import requests
import json
from common.pyTests import PyTestGenerics, GenericCRUDTest, GenericTest

from rest_framework import status


# Create your tests here.                                                                                                                                                                                 
django.setup()
serverUrl = PyTestGenerics.initPyTest()
print "using server url %s" % serverUrl

# ---------------------- UNIT TEST FOR BASIC CRUD OPERATIONS -------------

class PageViewCRUD(GenericCRUDTest, TestCase):
    sample = PageViewSample(serverUrl)
    partySample = PartySample(serverUrl)

    def setUp(self):
        super(PageViewCRUD, self).setUp()
        self.partyId = self.partySample.forcePost(self.partySample.data)
        self.sample.data['partyId']=self.sample.updateData['partyId']=self.partyId

    # update and delete are not allowed in this CRUD
    def test_for_update(self):
        pass

    def test_for_delete(self):
        pass

    def tearDown(self):
        super(PageViewCRUD, self).tearDown()
        PyTestGenerics.forceDelete(self.partySample.model, self.partySample.pkName, self.sample.data['partyId'])

# ----------------- END OF BASIC CRUD OPERATIONS ----------------------

class SessionCountViewTest(GenericTest, TestCase):
    url = serverUrl + 'session-logs/sessions/counts/'
    # sessionId, pageViewDate
    sampleData = [
        (1, '1979-01-01T00:00:00Z'),
        (1, '1980-01-01T00:00:00Z'),
        (1, '1981-01-01T00:00:00Z'),
        (1, '1982-01-01T00:00:00Z'),
        (2, '1980-01-01T00:00:00Z'),
        (3, '1980-01-01T00:00:00Z'),
        (3, '1981-01-01T00:00:00Z'),
    ]
    pageViewIdList = []
    sample = PageViewSample(serverUrl)
    partySample = PartySample(serverUrl)
    def setUp(self):
        super(SessionCountViewTest, self).setUp()
        self.partyId = self.partySample.forcePost(self.partySample.data)
        self.sample.data['partyId']=self.sample.updateData['partyId']=self.partyId
        for entry in self.sampleData:
            self.sample.data['sessionId'] = str(entry[0])
            self.sample.data['pageViewDate'] = entry[1]
            self.pageViewIdList.append(self.sample.forcePost(self.sample.data))

    def runTest(self, startDate, endDate, expectedCount):
        url = self.url + '?apiKey=%s' % self.apiKey
        if startDate:
            url += '&startDate=%s' % startDate
        if endDate:
            url += '&endDate=%s' % endDate
        cookies = {'apiKey':self.apiKey}
        req = requests.get(url,cookies=cookies)
        self.assertEqual(req.status_code, 200)
        count = req.json()['count']
        self.assertEqual(count, expectedCount)

    def test_for_get(self):
        self.runTest('1978-05-01T00:00:00Z', '1979-05-01T00:00:00Z', 1) #only sessionId 1
        self.runTest('1980-05-01T00:00:00Z', '1981-05-01T00:00:00Z', 2) #sessionId 1, 3
        self.runTest('1979-05-01T00:00:00Z', '1980-05-01T00:00:00Z', 3) #sessionId 1, 2, and 3

    def tearDown(self):
        super(SessionCountViewTest, self).setUp()
        PyTestGenerics.forceDelete(self.partySample.model, self.partySample.pkName, self.sample.data['partyId'])
        for entry in self.pageViewIdList:
            PyTestGenerics.forceDelete(self.sample.model, self.sample.pkName, entry)

print "Running unit tests on party web services API........."

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
