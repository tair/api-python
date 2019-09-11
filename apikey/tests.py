#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys
import requests
import json
from django.test import TestCase
from .models import ApiKey
from .testSamples import ApiKeySample
from common.tests import TestGenericInterfaces, GenericCRUDTest
from http.cookies import SimpleCookie

# Create your tests here.                                                                                                                                                                                 
django.setup()
serverUrl = TestGenericInterfaces.getHost()

# ---------------------- UNIT TEST FOR BASIC CRUD OPERATIONS -------------

class ApiKeyCRUD(GenericCRUDTest, TestCase):
    sample = ApiKeySample(serverUrl)

    def test_for_get_all(self):
        url = self.getUrl(self.sample.url)
        self.getAllHelper(url, 'apiKey', self.apiKey)

# ----------------- END OF BASIC CRUD OPERATIONS ----------------------

print("Running unit tests on API key web services API.........")

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
