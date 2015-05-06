#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys, getopt
from unittest import TestCase
from authorization.models import Pattern, AccessRule, AccessType
from partner.models import Partner
import requests
import json

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

def forceGet(obj, pk):
    try:
        filters = {obj.pkName:pk}
        return obj.model.objects.get(**filters)
    except:
        return None

def forceDelete(obj,pk):
    try:
        filters = {obj.pkName:pk}
        self.model.objects.get(**filters).delete()
    except:
        pass

def genericTestCreate(obj):
    req = requests.post(obj.url, data=obj.data)
    toDelete.append(req.json()[obj.pkName])
    obj.assertEqual(req.status_code, 201)
    obj.assertIsNotNone(forceGet(obj,req.json()[obj.pkName]))
    forceDelete(obj,req.json()[obj.pkName])

def genericTestGetAll(obj):
    pk = obj.forcePost(obj.data)
    url = obj.url
    if hasattr(obj, 'partnerId'):
        url += '?partnerId=%s' % obj.partnerId
    req = requests.get(url)
    toDelete.append(pk)
    obj.assertEqual(req.status_code, 200)
    forceDelete(obj,pk)

def genericTestUpdate(obj):
    pk = obj.forcePost(obj.data)
    url = obj.url + str(pk) + '/'
    if hasattr(obj, 'partnerId'):
        url += '?partnerId=%s' % obj.partnerId
    req = requests.put(url, data=obj.updateData)
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
    obj.assertIsNone(forceGet(obj,pk))

def genericTestGet(obj):
    pk = obj.forcePost(obj.data)
    url = obj.url + str(pk) + '/'
    if hasattr(obj, 'partnerId'):
        url += '?partnerId=%s' % obj.partnerId
    req = requests.get(url)
    toDelete.append(pk)
    obj.assertEqual(req.status_code, 200)
    forceDelete(obj,pk)

class PatternsCRUD(TestCase):
    url = serverUrl+'authorizations/patterns/'
    data = {
        'pattern':'/news/'
    }
    updateData = {
        'pattern':'/news2/'
    }
    pkName = 'patternId'
    model = Pattern
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
        u = self.model(pattern=data['pattern'])
        u.save()
        return u.patternId
       
    def tearDown(self):
        for d in toDelete:
            forceDelete(self,d)

class AccessRulesCRUD(TestCase):
    partnerId = 'tair'
    url = serverUrl+'authorizations/accessRules/'
    data = {
        'accessRuleId':1,
        'patternId':103,
        'accessTypeId':103,
        'partnerId':'tair',
    }

    updateData = {
        'accessRuleId':1,
        'patternId':104,
        'accessTypeId':104,
        'partnerId':'cdiff',
    }
    pkName = 'accessRuleId'
    model = AccessRule
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
        patternObj = Pattern.objects.get(patternId=data['patternId'])
        accessTypeObj = AccessType.objects.get(accessTypeId=data['accessTypeId'])
        partnerObj = Partner.objects.get(partnerId=data['partnerId'])
        u = self.model(patternId=patternObj,
                       accessTypeId=accessTypeObj,
                       partnerId=partnerObj,
        )
        u.save()
        return u.accessRuleId

    def tearDown(self):
        for d in toDelete:
            forceDelete(self,d)

class AccessTypesCRUD(TestCase):
    url = serverUrl+'authorizations/accessTypes/'
    data = {
        'name':'test1',
    }

    updateData = {
        'name':'test2',
    }
    pkName = 'accessTypeId'
    model = AccessType
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
        u = self.model(name=data['name'])
        u.save()
        return u.accessTypeId

    def tearDown(self):
        for d in toDelete:
            forceDelete(self,d)

print "Running unit tests on subscription web services API........."

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
