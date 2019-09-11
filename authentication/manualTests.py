#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys
import json
from django.test import TestCase, Client
from partner.testSamples import PartnerSample
from party.testSamples import UserPartySample
from common.tests import TestGenericInterfaces, GenericTest
from .testSamples import CredentialSample
from .tests import CredentialGenericTest
# Python 3: module Cookie -> http.cookies
from http.cookies import SimpleCookie

# Create your tests here.                                                                                                                                                                                 
django.setup()
serverUrl = TestGenericInterfaces.getHost()

# test for API endpoint /credentials/resetPwd/
class ResetPasswordTest(CredentialGenericTest):

    def test_for_reset_password(self):
        url = '%scredentials/resetPwd/?user=%s&partnerId=%s' % (serverUrl, self.sample.getUsername(), self.partnerId)

        # the default content type for put is 'application/octet-stream'
        # does not test for partyId update
        res = self.client.put(url, None, content_type='application/json')
        self.assertEqual(res.status_code, 200)        

print("Running unit tests on authentication/credential reset password web services API.........")

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)