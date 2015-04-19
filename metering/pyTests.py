#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.




from unittest import TestCase
import unittest

import django
from models import ipAddr, limits
import requests
import sys, getopt
# Create your tests here.
django.setup()

try:
    opts, args = getopt.getopt(sys.argv[1:], "h:" , ["host="])
except getopt.GetoptError:
    print "Usage: python -m metering.pyTests --host <hostname>\n\rExample hostname: 'http://52.4.81.100:8080/'"
    sys.exit(1)

serverUrl = ""
for opt, arg in opts:
    if opt=='--host' or opt=='-h':
        serverUrl = arg

if serverUrl=="":
    print "hostname is required"
    sys.exit(1)

testIP = '786.786.786.786'

print "Running tests for metering web service API...........\n"

class TestForIpAddr(TestCase):
    def test_for_getIPList(self):
        forcePostIP(testIP)
        req = requests.get(serverUrl+'meters/ip/')
        self.assertEqual(req.status_code, 200)
        boolean = False
        for ips in req.json():
            if ips['ip']==testIP:
                boolean = True
        self.assertEqual(boolean, True)
        forceDeleteIP(testIP)

    def test_for_getIPDetail(self):
        forcePostIP(testIP)
        req = requests.get(serverUrl+'meters/ip/'+testIP)
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json()['ip'], testIP)
        forceDeleteIP(testIP)

    def test_for_deleteIP(self):
        forcePostIP(testIP)
        req = requests.delete(serverUrl+'meters/ip/'+testIP)
        self.assertEqual(req.status_code, 204)

    def test_for_postIP(self):
        data = {'ip': testIP}
        req = requests.post(serverUrl+'meters/ip/', data=data)
        self.assertEqual(req.status_code, 201)
        ip = forceGetIP(testIP)
        self.assertIsNotNone(ip, not None)
        self.assertEqual(ip.ip, testIP)
        self.assertEqual(ip.count, 1)
        forceDeleteIP(testIP)

    def test_for_incrementIP(self):
        forcePostIP(testIP)
        req = requests.get(serverUrl+'meters/ip/'+testIP+'/increment')
        self.assertEqual(req.status_code, 200)
        ip = forceGetIP(testIP)
        self.assertEqual(ip.count, 2)
        forceDeleteIP(testIP)

    def test_for_IPlimit(self):
        forcePostIP(testIP)
        req = requests.get(serverUrl+'meters/ip/'+testIP+'/limit')
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json()['status'], "OK")
        setCount = limits.objects.using('mySQLTest').get(name="WarningLimit").val
        forceSetIP(testIP, setCount)
        req = requests.get(serverUrl+'meters/ip/'+testIP+'/limit')
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json()['status'], "Warning")
        setCount = limits.objects.using('mySQLTest').get(name="MeteringLimit").val 
        forceSetIP(testIP, setCount)
        req = requests.get(serverUrl+'meters/ip/'+testIP+'/limit')
        self.assertEqual(req.status_code, 200)
        self.assertEqual(req.json()['status'], "Block")
        forceDeleteIP(testIP)

    def test_for_deleteAll(self):
        pass

    def tearDown(self):
        for ips in ipAddr.objects.all():
            if (ips.ip==testIP):
                ips.delete()

class TestForLimits(TestCase):
    def test_for_getWarningLimit(self):
        req = requests.get(serverUrl+'meters/limits/warningLimit')
        self.assertEqual(req.status_code, 200)

    def test_for_getMeteringLimit(self):
        req = requests.get(serverUrl+'meters/limits/meteringLimit')
        self.assertEqual(req.status_code, 200)

    def test_for_setWarningLimit(self):
        pass

    def test_for_setMeteringLimit(self):
        pass


#Auxillary functions
def forcePostIP(ip):
    try:
        ipAddr.objects.using('mySQLTest').get(ip=ip)
    except:
        u = ipAddr(ip=ip, count=1)
        u.save(using='mySQLTest')

def forceDeleteIP(ip):
    try:
        u = ipAddr.objects.using('mySQLTest').get(ip=ip)
        u.delete(using='mySQLTest')
    except:
        pass

def forceGetIP(ips):
    try:
        u = ipAddr.objects.using('mySQLTest').get(ip=ips)
        return u
    except:
        return None

def forceSetIP(ip, count):
    u = ipAddr.objects.using('mySQLTest').get(ip=ip)
    u.count = count
    u.save(using='mySQLTest')


if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
