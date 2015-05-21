#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys, getopt
from unittest import TestCase
from party.models import Party, IpRange
import requests
import json
from testSamples import PartySample, IpRangeSample
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

print "Running unit tests on party web services API........."

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
