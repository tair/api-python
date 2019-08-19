import requests
import json
import sys, getopt

from testSamples import CommonApiKeySample
from partner.models import Partner
from apikey.models import ApiKey
from django.test import Client
from django.conf import settings
# Python 3: module Cookie -> http.cookies
from Cookie import SimpleCookie

class GenericTest(object):
    apiKeySample = CommonApiKeySample()
    apiKey = None
    def setUp(self):
        #delete possible entries that we use as test case
        ApiKey.objects.filter(apiKey=self.apiKeySample.data['apiKey']).delete()
        self.apiKeyId = self.apiKeySample.forcePost(self.apiKeySample.data)
        self.apiKey = self.apiKeySample.data['apiKey']

# This function checks if sampleData is within the array of data retrieved
# from API call.
def checkMatch(sampleData, retrievedDataArray, pkName, pk):
    hasMatch = False
    for item in retrievedDataArray:
        # find the entry from dataArray that has the same PK
        # as the entry created
        if item[pkName] == pk:
            hasMatch = True
            for key in sampleData:
                # makes sure that all contents from sample is the
                # same as content retrieved from request
                if not (item[key] == sampleData[key] or float(item[key]) == float(sampleData[key])):
                    hasMatch = False
                    break
    return hasMatch

class GenericGETOnlyTest(GenericTest):
    client = Client()

    def test_for_get_all(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = sample.url
        if self.apiKey:
            url = url+'?apiKey=%s' % (self.apiKey)

        self.client.cookies = SimpleCookie({'apiKey':self.apiKey})
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(checkMatch(sample.data, json.loads(res.content), sample.pkName, pk), True)

    def test_for_get(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = sample.url + '?%s=%s' % (sample.pkName, str(pk))
        if self.apiKey:
            url = url+'&apiKey=%s' % (self.apiKey)
        
        self.client.cookies = SimpleCookie({'apiKey':self.apiKey})
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(checkMatch(sample.data, json.loads(res.content), sample.pkName, pk), True)

class GenericCRUDTest(GenericGETOnlyTest):
    client = Client()

    # GET tests defined in GenericGETOnlyTest class

    def test_for_create(self):
        sample = self.sample
        url = sample.url
        if self.apiKey:
            url = url+'?apiKey=%s' % (self.apiKey)

        self.client.cookies = SimpleCookie({'apiKey':self.apiKey})
        res = self.client.post(url, sample.data)

        self.assertEqual(res.status_code, 201)
        self.assertIsNotNone(PyTestGenerics.forceGet(sample.model,sample.pkName,json.loads(res.content)[sample.pkName]))

    def test_for_update(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = sample.url + '?%s=%s' % (sample.pkName, str(pk))
        if self.apiKey:
            url = url+'&apiKey=%s' % (self.apiKey)
        if sample.pkName in sample.updateData:
            pk = sample.updateData[sample.pkName]

        self.client.cookies = SimpleCookie({'apiKey':self.apiKey})
        # the default content type for put is 'application/octet-stream'
        res = self.client.put(url, json.dumps(sample.updateData), content_type='application/json')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(checkMatch(sample.updateData, json.loads(res.content), sample.pkName, pk), True)

    def test_for_delete(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)

        url = sample.url + '?%s=%s' % (sample.pkName, str(pk))
        if self.apiKey:
            url = url+'&apiKey=%s' % (self.apiKey)

        self.client.cookies = SimpleCookie({'apiKey':self.apiKey})
        res = self.client.delete(url)

        self.assertIsNone(PyTestGenerics.forceGet(sample.model,sample.pkName,pk))

class PyTestGenerics:
    @staticmethod
    def initPyTest():
        if hasattr(settings, 'HOSTNAME'):
            return settings.HOSTNAME
        # default connection to localhost
        return "http://localhost/"

    @staticmethod
    def forceGet(model, pkName, pk):
        try:
            filters = {pkName:pk}
            return model.objects.get(**filters)
        except:
            return None

    @staticmethod
    def forceDelete(model, pkName,pk):
        try:
            filters = {pkName:pk}
            model.objects.get(**filters).delete()
        except:
            pass

    @staticmethod
    def forcePost(model, pkName, data):
        u = model(**data)
        u.save()
        return u.__dict__[pkName]
