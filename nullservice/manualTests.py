import django
import unittest
import sys
import json

from django.test import TestCase
from common.tests import TestGenericInterfaces, GenericTest
from http.cookies import SimpleCookie

# Create your tests here.
django.setup()
serverUrl = TestGenericInterfaces.getHost()

# test for API end point /nullservice
class NullServiceTest(GenericTest, TestCase):
    def test_for_get(self):
        url = '%snullservice/' % (serverUrl)

        self.client.cookies = SimpleCookie({'apiKey':self.apiKey})
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

print("Running unit tests on nullservice web services API.........")

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)