#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys, getopt
from unittest import TestCase
from subscription.models import Subscription, Party, IpRange, SubscriptionTransaction
from partner.models import Partner
import requests
import json

import copy

# Create your tests here.                                                                                                                                                                                 
django.setup()

try:
    opts, args = getopt.getopt(sys.argv[1:], "h:" , ["host="])
except getopt.GetoptError:
    print "Usage: python -m metering.pyTests --host <hostname>\n\rExample hostname: 'http://pb.steveatgetexp.com:8080/'"
    sys.exit(1)

serverUrl = ""
for opt, arg in opts:
    if opt=='--host' or opt=='-h':
        serverUrl = arg

if serverUrl=="":
    print "hostname is required"
    sys.exit(1)

toDelete = []

print "using server url %s" % serverUrl

def forceGet(obj, pk):
    try:
        filters = {obj.pkName:pk}
        return obj.model.objects.get(**filters)
    except:
        return None

def forceDelete(obj,pk):
    try:
        filters = {obj.pkName:pk}
        obj.model.objects.get(**filters).delete()
    except:
        pass

def genericTestCreate(obj):
    req = requests.post(obj.url, data=obj.data)
    toDelete.append(req.json()[obj.pkName])
    obj.assertEqual(req.status_code, 201)
    obj.assertIsNotNone(forceGet(obj, req.json()[obj.pkName]))
    forceDelete(obj, req.json()[obj.pkName])

def genericTestGetAll(obj):
    pk = obj.forcePost(obj.data)
    url = obj.url
    if hasattr(obj, 'partnerId'):
        url += '?partnerId=%s' % obj.partnerId
    req = requests.get(url)
    toDelete.append(pk)
    obj.assertEqual(req.status_code, 200)
    forceDelete(obj, pk)

def genericTestUpdate(obj):
    pk = obj.forcePost(obj.data)
    url = obj.url + str(pk) + '/'
    if hasattr(obj, 'partnerId'):
        url += '?partnerId=%s' % obj.partnerId
    req = requests.put(url, data=obj.updateData)

    if obj.pkName in obj.updateData:
        pk = obj.updateData[obj.pkName]
    toDelete.append(pk)
    obj.assertEqual(req.status_code, 200)
    forceDelete(obj,pk)

def genericTestDelete(obj):
    pk = obj.forcePost(obj.data)
    url = obj.url + str(pk) + '/'
    if hasattr(obj, 'partnerId'):
        url += '?partnerId=%s' % obj.partnerId
    req = requests.delete(url)
    toDelete.append(pk)
    obj.assertIsNone(forceGet(obj, pk))

def genericTestGet(obj):
    pk = obj.forcePost(obj.data)
    url = obj.url + str(pk) + '/'
    if hasattr(obj, 'partnerId'):
        url += '?partnerId=%s' % obj.partnerId
    req = requests.get(url)
    toDelete.append(pk)
    obj.assertEqual(req.status_code, 200)
    forceDelete(obj,pk)

class SubscriptionCRUD(TestCase):
    partnerId = 'tair'
    url = serverUrl+'subscriptions/'
    data = {
        'startDate':'2012-04-12T00:00:00Z',
        'endDate':'2018-04-12T00:00:00Z',
        'partnerId':'tair',
        'partyId':1,
    }
    updateData = {
        'startDate':'2012-04-12T00:00:00Z',
        'endDate':'2018-04-12T00:00:00Z',
        'partnerId':'cdiff',
        'partyId':1,
    }
    pkName = 'subscriptionId'
    model = Subscription
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

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partyId'] = Party.objects.get(partyId=self.data['partyId'])
        postData['partnerId'] = Partner.objects.get(partnerId=self.data['partnerId'])
        u = self.model(**postData)
        u.save()
        return u.subscriptionId
       
    def tearDown(self):
        for d in toDelete:
            forceDelete(self, d)

class SubscriptionTransactionCRUD(TestCase):
    url = serverUrl+'subscriptions/transactions/'
    data = {
        'subscriptionId':1,
        'transactionDate':'2012-04-12T00:00:00Z',
        'startDate':'2012-04-12T00:00:00Z',
        'endDate':'2018-04-12T00:00:00Z',
        'transactionType':'Initial',
    }
    updateData = {
        'subscriptionId':1,
        'transactionDate':'2014-02-12T00:00:00Z',
        'startDate':'2012-04-12T00:00:00Z',
        'endDate':'2018-04-12T00:00:00Z',
        'transactionType':'Renew',
    }
    pkName = 'subscriptionTransactionId'
    model = SubscriptionTransaction
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

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['subscriptionId'] = Subscription.objects.get(subscriptionId=data['subscriptionId'])
        u = self.model(**postData)
        u.save()
        return u.subscriptionTransactionId

    def tearDown(self):
        for d in toDelete:
            forceDelete(self, d)

class PartyCRUD(TestCase):
    url = serverUrl+'subscriptions/parties/'
    data = {
        'partyType':'user',
    }
    updateData = {
        'partyType':'organization',
    }
    pkName = 'partyId'
    model = Party
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

    def forcePost(self,data):
        u = self.model(**data)
        u.save()
        return u.partyId

    def tearDown(self):
        for d in toDelete:
            forceDelete(self, d)

class IpRangeCRUD(TestCase):
    url = serverUrl+'subscriptions/ipranges/'
    data = {
        'start':'120.0.0.0',
        'end':'120.255.255.255',
        'partyId':1
    }
    updateData = {
        'start':'120.0.0.0',
        'end':'120.255.211.200',
        'partyId':1
    }
    pkName = 'ipRangeId'
    model = IpRange
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

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partyId'] = Party.objects.get(partyId=data['partyId'])
        u = self.model(**postData)
        u.save()
        return u.ipRangeId

    def tearDown(self):
        for d in toDelete:
            forceDelete(self, d)

print "Running unit tests on subscription web services API........."

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
