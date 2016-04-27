import requests
import json
import sys, getopt

from testSamples import CommonApiKeySample
from partner.models import Partner
from apikey.models import ApiKey

class GenericTest(object):
    apiKeySample = CommonApiKeySample()
    apiKey = None
    def setUp(self):
        #delete possible entries that we use as test case
        ApiKey.objects.filter(apiKey=self.apiKeySample.data['apiKey']).delete()
        self.apiKeyId = self.apiKeySample.forcePost(self.apiKeySample.data)
        self.apiKey = self.apiKeySample.data['apiKey']

    def tearDown(self):
        PyTestGenerics.forceDelete(self.apiKeySample.model, self.apiKeySample.pkName, self.apiKeyId)

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
                if not (item[key] == sampleData[key] or float(item[key])==float(sampleData[key])):
                    hasMatch = False
                    break
    return hasMatch

class GenericCRUDTest(GenericTest):
    def test_for_create(self):
        sample = self.sample
        url = sample.url
        credentialId = '2'
        secretKey = '7DgskfEF7jeRGn1h+5iDCpvIkRA='
        # if self.apiKey:
        #     url = url+'?apiKey=%s' % (self.apiKey)+'&credentialId='+credentialId+'&secretKey='+secretKey
        url = url+'&credentialId='+credentialId+'&secretKey='+secretKey
        cookies = {'apiKey':self.apiKey}
        req = requests.post(url, data=sample.data, cookies=cookies)

        self.assertEqual(req.status_code, 201)
        self.assertIsNotNone(PyTestGenerics.forceGet(sample.model,sample.pkName,req.json()[sample.pkName]))
        PyTestGenerics.forceDelete(sample.model,sample.pkName,req.json()[sample.pkName])

    def test_for_get_all(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = sample.url
        if self.apiKey:
            url = url+'?apiKey=%s' % (self.apiKey)
        cookies = {'apiKey':self.apiKey}
        req = requests.get(url, cookies=cookies)
        self.assertEqual(req.status_code, 200)
        self.assertEqual(checkMatch(sample.data, req.json(), sample.pkName, pk), True)

        PyTestGenerics.forceDelete(sample.model,sample.pkName,pk)

    def test_for_update(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = sample.url + '?%s=%s' % (sample.pkName, str(pk))
        if self.apiKey:
            url = url+'&apiKey=%s' % (self.apiKey)
        cookies = {'apiKey':self.apiKey}
        req = requests.put(url, data=sample.updateData,cookies=cookies)
        if sample.pkName in sample.updateData:
            pk = sample.updateData[sample.pkName]
        self.assertEqual(req.status_code, 200)
        self.assertEqual(checkMatch(sample.updateData, req.json(), sample.pkName, pk), True)
        PyTestGenerics.forceDelete(sample.model,sample.pkName,pk)

    def test_for_delete(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = sample.url + '?%s=%s' % (sample.pkName, str(pk))
        if self.apiKey:
            url = url+'&apiKey=%s' % (self.apiKey)
        cookies = {'apiKey':self.apiKey}
        req = requests.delete(url, cookies=cookies)
        self.assertIsNone(PyTestGenerics.forceGet(sample.model,sample.pkName,pk))

    def test_for_get(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = sample.url + '?%s=%s' % (sample.pkName, str(pk))
        if self.apiKey:
            url = url+'&apiKey=%s' % (self.apiKey)
        cookies = {'apiKey':self.apiKey}
        req = requests.get(url, cookies=cookies)
        self.assertEqual(req.status_code, 200)
        self.assertEqual(checkMatch(sample.data, req.json(), sample.pkName, pk), True)
        PyTestGenerics.forceDelete(sample.model,sample.pkName,pk)

class PyTestGenerics:
    @staticmethod
    def initPyTest():
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
        return serverUrl


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
