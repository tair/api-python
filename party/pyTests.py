#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys, getopt
from unittest import TestCase
from models import Party, IpRange
import requests
import json
from testSamples import PartySample, IpRangeSample, PartyAffiliationSample
from common.pyTests import PyTestGenerics, GenericCRUDTest, GenericTest


# Create your tests here.                                                                                                                                                                                 
django.setup()
serverUrl = PyTestGenerics.initPyTest()
print "using server url %s" % serverUrl

# ---------------------- UNIT TEST FOR BASIC CRUD OPERATIONS -------------

class PartyCRUD(GenericTest, TestCase):
    sample = PartySample(serverUrl)

    def test_for_get(self):
        credentialId = "2"
        partyId = "3"
        secretKey = "7DgskfEF7jeRGn1h%2B5iDCpvIkRA%3D"

        sample = self.sample
        url = sample.url
        if self.apiKey:
            url = url+'?credentialId=%s&secretKey=%s&partyId=%s' % (credentialId, secretKey, partyId)
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        expectedOutput = {u'name': u'Liu Jiaming', u'country': 10, u'consortiums': [], u'partyType': u'user', u'partyId': 3, u'display': True}
        rJson = response.json()[0]
        isEqual = True
        for key in expectedOutput:
            if not key in rJson:
                isEqual = False
            if not expectedOutput[key] == rJson[key]:
                isEqual = False
        self.assertEqual(isEqual, True)

class InstitutionCRUD(GenericTest, TestCase):
    credentialId = "2"
    partyId = "3"
    secretKey = "7DgskfEF7jeRGn1h%2B5iDCpvIkRA%3D"

    def test_for_get(self):
        if self.apiKey:
            url = serverUrl+'parties/institutions/?credentialId=%s&secretKey=%s&partyId=%s' % (self.credentialId, self.secretKey, self.partyId)
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)

        expectedOutput = [{u'name': u'Liu Jiaming', u'country': 10, u'consortiums': [], u'partyType': u'user', u'partyId': 3, u'display': True}, {u'username': u' Agricultural Sciences', u'institution': None, u'partnerId': u'tair', u'userIdentifier': u'1501491328', u'partyId': 3, u'password': u'c984aed014aec7623a54f0591da07a85fd4b762d', u'email': u'jm_liu2013@163.com'}]
        rJson = response.json()
#        print "-------"
#        print expectedOutput
#        print rJson
#        print "-------"
        isEqual = expectedOutput == rJson
        self.assertEqual(isEqual, True)

    def test_for_create(self):
        data = {
            "username":"bb4",
            "partnerId":"tair",
            "partyType":"organization",
        }
        url = serverUrl+'parties/institutions/?credentialId=%s&secretKey=%s' % (self.credentialId, self.secretKey)
        req = requests.post(url, data=data)

        self.assertEqual(req.status_code, 201)
        #self.assertIsNotNone(PyTestGenerics.forceGet(sample.model,sample.pkName,req.json()[sample.pkName]))
        PyTestGenerics.forceDelete(Party,'partyId',req.json()[0]['partyId'])


class IpRangeCRUD(GenericCRUDTest, TestCase):
    sample = IpRangeSample(serverUrl)
    partySample = PartySample(serverUrl)

    def setUp(self):
        super(IpRangeCRUD,self).setUp()
        partyId = self.partySample.forcePost(self.partySample.data)
        self.sample.data['partyId']=self.sample.updateData['partyId']=partyId

    def tearDown(self):
        super(IpRangeCRUD,self).tearDown()
        PyTestGenerics.forceDelete(self.partySample.model, self.partySample.pkName, self.sample.data['partyId'])

class PartyAffiliationCRUD(GenericCRUDTest, TestCase):
    sample = PartyAffiliationSample(serverUrl)

    def test_for_update(self):
        pass

    def test_for_get_all(self):
        pass

    # def test_for_create(self):
    #     pass

    def test_for_delete(self):
        pass

# ----------------- END OF BASIC CRUD OPERATIONS ----------------------



print "Running unit tests on party web services API........."

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
