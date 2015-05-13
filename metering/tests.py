#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.





from django.test import TestCase

from .models import ipAddr
import requests
# Create your tests here.
serverUrl = 'http://52.4.106.144:8080/'
testIP = '786.786.786.786'

class TestForIpAddr(TestCase):
#    def test_for_getIPList(self):
#        forcePostIP(testIP)
#        req = requests.get(serverUrl+'meters/ip/')
#        boolean = False
#        for ips in req.json():
#            if ips['ip']==testIP:
#                boolean = True
#        self.assertEqual(boolean, True)
#        forceDeleteIP(testIP)
#
#    def test_for_getIPDetail(self):
#        forcePostIP(testIP)
#        req = requests.get(serverUrl+'meters/ip/'+testIP)
#        self.assertEqual(req.status_code, 200)
#        forceDeleteIP(testIP)

#    def test_for_deleteIP(self):
#        forcePostIP(testIP)
#        req = requests.delete(serverUrl+'/meters/ip/'+testIP)
#        self.assertEqual(req.status_code, 204)

    def test_for_postIP(self):
        data = {'ip': testIP}
        req = requests.post(serverUrl+'meters/ip/', data=data)
        self.assertEqual(req.status_code, 201)
        ip = forceGetIP(testIP)
        self.assertEqual(ip, not None)
        self.assertEqual(ip.ip, testIP)
        self.assertEqual(ip.count, 1)
        forceDeleteIP(testIP)

#    def test_for_incrementIP(self):
#        forcePostIP(testIP)
#        req = requests.get(serverUrl+'/meters/ip/'+testIP+'/increment')
#        self.assertEqual(req.status_code, 200)
#        ip = forceGetIP(testIP)
#        self.assertEqual(ip.count, 2)
#        forceDeleteIP(testIP)

#    def test_for_atWarningLimit(self):
#        forcePostIP(testIP)
#        req = requests.get(serverUrl+'/meters/ip/'+testIP+'/atWarningLimit')
#        self.assertEqual(req.json()['bool'], False)
#        forceSetIP(testIP, 9)
#        req = requests.get(serverUrl+'/meters/ip/'+testIP+'/atWarningLimit')
#        self.assertEqual(req.json()['bool'],True)
#        forceDeleteIP(testIP)
#
#    def test_for_atMeteringLimit(self):
#        forcePostIP(testIP)
#        req = requests.get(serverUrl+'/meters/ip/'+testIP+'/atMeteringLimit')
#        self.assertEqual(req.json()['bool'], False)
#        forceSetIP(testIP, 11)
#        req = requests.get(serverUrl+'/meters/ip/'+testIP+'/atMeteringLimit')
#        self.assertEqual(req.json()['bool'],True)
#        forceDeleteIP(testIP)


class TestForLimits(TestCase):
    def test_for_getWarningLimit(self):
        pass

    def test_for_getMeteringLimit(self):
        pass

    def test_for_setWarningLimit(self):
        pass

    def test_for_setMeteringLimit(self):
        pass


#Auxillary functions
def forcePostIP(ip):
    #try:
    #    ipAddr.objects.get(ip=ip)
    #except:
        u = ipAddr(ip=ip, count=1)
        u.save()

def forceDeleteIP(ip):
    try:
        u = ipAddr.objects.get(ip=ip)
        u.delete()
    except:
        pass

def forceGetIP(ip):
    try:
        u = ipAddr.objects.get(ip=ip)
        return u
    except:
        return None

def forceSetIP(ip, count):
    u = ipAddr.objects.get(ip=ip)
    u.count = count
    u.save()

