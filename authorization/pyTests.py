#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys, getopt
from unittest import TestCase
from authorization.models import Pattern, AccessRule, AccessType
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

def genericTestCreate(obj):
    req = requests.post(obj.url, data=obj.data)
    toDelete.append(req.json()[obj.pkName])
    obj.assertEqual(req.status_code, 201)
    obj.assertIsNotNone(obj.forceGet(req.json()[obj.pkName]))
    obj.forceDelete(req.json()[obj.pkName])

def genericTestGetAll(obj):
    pk = obj.forcePost(obj.data)
    req = requests.get(obj.url)
    toDelete.append(pk)
    obj.assertEqual(req.status_code, 200)
    obj.forceDelete(pk)

def genericTestUpdate(obj):
    pk = obj.forcePost(obj.data)
    req = requests.put(obj.url+str(pk)+'/', data=obj.updateData)
    toDelete.append(pk)
    obj.assertEqual(req.status_code, 200)
    obj.forceDelete(pk)

def genericTestDelete(obj):
    pk = obj.forcePost(obj.data)
    req = requests.delete(obj.url+str(pk))
    toDelete.append(pk)
    obj.assertIsNone(obj.forceGet(pk))

def genericTestGet(obj):
    pk = obj.forcePost(obj.data)
    req = requests.get(obj.url+str(pk))
    toDelete.append(pk)
    obj.assertEqual(req.status_code, 200)
    obj.forceDelete(pk)

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

    def forceGet(self,pk):
        try:
            return self.model.objects.get(patternId=pk)
        except:
            return None

    def forcePost(self,data):
        u = self.model(pattern=data['pattern'])
        u.save()
        return u.patternId
       
    def forceDelete(self,pk):
        try:
            self.model.objects.get(patternId=pk).delete()
        except:
            pass

    def tearDown(self):
        for d in toDelete:
            self.forceDelete(d)

class AccessRulesCRUD(TestCase):
    url = serverUrl+'authorizations/accessRules/'
    data = {
        'patternId':1,
        'accessTypeId':1
    }

    updateData = {
        'patternId':2,
        'accessTypeId':2
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

    def forceGet(self,pk):
        try:
            return self.model.objects.get(accessRuleId=pk)
        except:
            return None

    def forcePost(self,data):
        patternObj = Pattern.objects.get(patternId=data['patternId'])
        accessTypeObj = AccessType.objects.get(accessTypeId=data['accessTypeId'])
        u = self.model(patternId=patternObj,
                       accessTypeId=accessTypeObj)
        u.save()
        return u.accessRuleId

    def forceDelete(self,pk):
        try:
            self.model.objects.get(accessRuleId=pk).delete()
        except:
            pass

    def tearDown(self):
        for d in toDelete:
            self.forceDelete(d)

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

    def forceGet(self,pk):
        try:
            return self.model.objects.get(accessTypeId=pk)
        except:
            return None

    def forcePost(self,data):
        u = self.model(name=data['name'])
        u.save()
        return u.accessTypeId

    def forceDelete(self,pk):
        try:
            self.model.objects.get(accessTypeId=pk).delete()
        except:
            pass

    def tearDown(self):
        for d in toDelete:
            self.forceDelete(d)

print "Running unit tests on subscription web services API........."

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
