#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys
import requests
import json
from django.test import TestCase
from models import ApiKey
from testSamples import ApiKeySample
from common.pyTests import PyTestGenerics, GenericCRUDTest, checkMatch
# Python 3: module Cookie -> http.cookies
from Cookie import SimpleCookie

# Create your tests here.                                                                                                                                                                                 
django.setup()
serverUrl = PyTestGenerics.initPyTest()

# ---------------------- UNIT TEST FOR BASIC CRUD OPERATIONS -------------

class ApiKeyCRUD(GenericCRUDTest, TestCase):
    sample = ApiKeySample(serverUrl)

    def test_for_get_all(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = sample.url
        if self.apiKey:
            self.client.cookies = SimpleCookie({'apiKey':self.apiKey})

        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

        apiKeyArray = json.loads(res.content)

        for item in apiKeyArray:
            # skip for common api key
            if item['apiKey'] == self.apiKey:
                continue;
            else:
                self.assertEqual(sample.data['apiKey'] == item['apiKey'], True)
                self.assertEqual(pk == item[sample.pkName], True)

# ----------------- END OF BASIC CRUD OPERATIONS ----------------------

print "Running unit tests on API key web services API........."

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
