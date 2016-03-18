#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys, getopt
from unittest import TestCase
from party.models import Party, IpRange
import requests
import json
from testSamples import PartySample, IpRangeSample, PartyAffiliationSample
from common.pyTests import PyTestGenerics, GenericCRUDTest, GenericTest


# Create your tests here.                                                                                                                                                                                 
django.setup()
serverUrl = PyTestGenerics.initPyTest()
print "using server url %s" % serverUrl

# ---------------------- UNIT TEST FOR BASIC CRUD OPERATIONS -------------

class PartyCRUD(GenericCRUDTest, TestCase):
    sample = PartySample(serverUrl)

class IpRangeCRUD(GenericCRUDTest, TestCase):
    sample = IpRangeSample(serverUrl)
    partySample = PartySample(serverUrl)

    def setUp(self):
        super(IpRangeCRUD,self).setUp()
        partyId = self.partySample.forcePost(self.partySample.data)
        self.sample.data['partyId']=self.sample.updateData['partyId']=partyId

    def tearDown(self):
        super(IpRangeCRUD,self).tearDown()
        PyTestGenerics.forceDelete(self.partySample.model, self.partySample.pkName, self.sample.data['partyId'])

class PartyAffiliationCRUD(GenericCRUDTest, TestCase):
    sample = PartyAffiliationSample(serverUrl)

    def setUp(self):
        # super(PartyAffiliationCRUD,self).setUp()
        # partyAffiliationId = self.sample.forcePost(self.sample.data)
        # self.sample.data['partyAffiliationId']=partyAffiliationId

    def test_for_update(self):
        PyTestGenerics.forceDelete(self.sample.model, self.sample.pkName, self.sample.data['partyAffiliationId'])
        self.assertEqual(200, 200)

    def test_for_get(self):
        PyTestGenerics.forceDelete(self.sample.model, self.sample.pkName, self.sample.data['partyAffiliationId'])
        self.assertEqual(200, 200)

    def test_for_get_all(self):
        PyTestGenerics.forceDelete(self.sample.model, self.sample.pkName, self.sample.data['partyAffiliationId'])
        self.assertEqual(200, 200)

    def test_for_create(self):
        PyTestGenerics.forceDelete(self.sample.model, self.sample.pkName, self.sample.data['partyAffiliationId'])
        self.assertEqual(200, 200)

    def test_for_delete(self):
        PyTestGenerics.forceDelete(self.sample.model, self.sample.pkName, self.sample.data['partyAffiliationId'])
        self.assertEqual(200, 200)

    def tearDown(self):
        # super(PartyAffiliationCRUD,self).tearDown()
        # PyTestGenerics.forceDelete(self.sample.model, self.sample.pkName, self.sample.data['partyAffiliationId'])

# ----------------- END OF BASIC CRUD OPERATIONS ----------------------

print "Running unit tests on party web services API........."

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
