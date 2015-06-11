#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys, getopt
from unittest import TestCase
import requests
import json
from models import ApiKey
from testSamples import ApiKeySample
from common.pyTests import PyTestGenerics, GenericCRUDTest

# Create your tests here.                                                                                                                                                                                 
django.setup()
serverUrl = PyTestGenerics.initPyTest()
print "using server url %s" % serverUrl

# ---------------------- UNIT TEST FOR BASIC CRUD OPERATIONS -------------

class ApiKeyCRUD(GenericCRUDTest, TestCase):
    sample = ApiKeySample(serverUrl)

    def setUp(self):
#        super(ApiKeyCRUD, self).setUp()
        ApiKey.objects.filter(apiKey=self.sample.data['apiKey']).delete()
        ApiKey.objects.filter(apiKey=self.sample.updateData['apiKey']).delete()

    # overrides parent class teardown.
    def tearDown(self):
        pass
# ----------------- END OF BASIC CRUD OPERATIONS ----------------------

print "Running unit tests on party web services API........."

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
