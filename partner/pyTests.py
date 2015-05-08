#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys, getopt
from unittest import TestCase
from partner.models import Partner, PartnerPattern, SubscriptionTerm
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
        pass

def forceDelete(obj,pk):
    filters = {obj.pkName:pk}
    try:
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
    toDelete.append(pk)
    obj.assertEqual(req.status_code, 200)
    if obj.pkName in obj.updateData:
        pk = obj.updateData[obj.pkName]
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

class PartnerCRUD(TestCase):
    url = serverUrl+'partners/'
    data = {
        'partnerId':'test',
        'name':'testPartner',
    }
    updateData = {
        'partnerId':'test1',
        'name':'testPartner2',
    }
    pkName = 'partnerId'
    model = Partner
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
        return u.partnerId
       
    def tearDown(self):
        for d in toDelete:
            forceDelete(self, d)

class PartnerPatternCRUD(TestCase):
    url = serverUrl+'partners/patterns/'
    partnerId = 'cdiff'
    data = {
        'partnerId':'cdiff',
        'pattern':'/test/',
    }
    updateData = {
        'partnerId':'tair',
        'pattern':'/test2/',
    }
    pkName = 'partnerPatternId'
    model = PartnerPattern
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
        postData['partnerId'] = Partner.objects.get(partnerId=data['partnerId'])
        u = self.model(**postData)
        u.save()
        return u.partnerPatternId

    def tearDown(self):
        for d in toDelete:
            forceDelete(self, d)


class SubscriptionTermCRUD(TestCase):
    partnerId='tair'
    url = serverUrl+'partners/terms/'
    data = {
        'partnerId':'tair',
        'period':180,
        'price':360.00,
        'groupDiscountPercentage':0.7,
        'autoRenew':False,
    }
    updateData = {
        'partnerId':'tair',
        'period':365,
        'price':180.00,
        'groupDiscountPercentage':0.8,
        'autoRenew':True,
    }
    pkName = 'subscriptionTermId'
    model = SubscriptionTerm
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
        postData['partnerId'] = Partner.objects.get(partnerId=data['partnerId'])
        u = self.model(**postData)
        u.save()
        return u.subscriptionTermId

    def tearDown(self):
        for d in toDelete:
            forceDelete(self, d)

print "Running unit tests on subscription web services API........."

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
