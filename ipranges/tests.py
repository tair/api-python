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

# test for API end point /ipranges/validateip
class ValidateIpTest(GenericTest, TestCase):
    VALID_PUBLIC_IPV4 = '74.9.8.38'
    VALID_PRIVATE_IPV4 = '172.16.5.0'
    VALID_IPV6_FULL = '2001:0db8:0000:0000:0000:8a2e:0370:7334'
    VALID_IPV6_SIMPLIFIED = '2001:db8::8a2e:370:7334'
    INVALID_IP_I = '67.2.6'
    INVALID_IP_II = '123.276.4.1'
    INVALID_IP_III = '124.89.7.65.1'
    INVALID_IP_IV = 'random_string'
    INVALID_IP_V = 99999

    def test_for_get(self):
        self.assert_for_valid_ip(self.VALID_PUBLIC_IPV4, 4)
        self.assert_for_valid_ip(self.VALID_PRIVATE_IPV4, 4)
        self.assert_for_valid_ip(self.VALID_IPV6_FULL, 6)
        self.assert_for_valid_ip(self.VALID_IPV6_SIMPLIFIED, 6)
        self.assert_for_invalid_ip(self.INVALID_IP_I)
        self.assert_for_invalid_ip(self.INVALID_IP_II)
        self.assert_for_invalid_ip(self.INVALID_IP_III)
        self.assert_for_invalid_ip(self.INVALID_IP_IV)
        self.assert_for_invalid_ip(self.INVALID_IP_V)

    def assert_for_valid_ip(self, ip, ipVersion):
        res = self.get_response(ip)

        self.assertEqual(res.status_code, 200)
        # The raw response will be bytes so need to convert to string and then compare
        self.assertEqual(res.content.decode(), '{"ip version": %s}' % ipVersion)

    def assert_for_invalid_ip(self, ip):
        res = self.get_response(ip)

        self.assertEqual(res.status_code, 200)
        # The raw response will be bytes so need to convert to string and then compare
        self.assertEqual(res.content.decode(), '{"ip": "invalid"}')

    # TODO: find example that can trigger this response
    def assert_for_error_input(self, ip):
        res = self.get_response(ip)

        self.assertEqual(res.status_code, 200)
        # The raw response will be bytes so need to convert to string and then compare
        self.assertEqual(res.content.decode(), '{"ip": "error"}')

    def get_response(self, ip):
        url = '%sipranges/validateip/?ip=%s' % (serverUrl, ip)

        self.client.cookies = SimpleCookie({'apiKey':self.apiKey})
        res = self.client.get(url)

        return res

print("Running unit tests on IP range web services API.........")

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)