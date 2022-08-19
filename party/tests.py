#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                              
import django
import unittest
import sys
import json
import copy
from django.test import TestCase, Client
from .testSamples import CountrySample, UserPartySample, OrganizationPartySample, InstitutionPartySample, ConsortiumPartySample, IpRangeSample, PartyAffiliationSample
from partner.testSamples import PartnerSample
from subscription.testSamples import SubscriptionSample
from authentication.testSamples import CredentialSample
from common.tests import TestGenericInterfaces, GenericGETOnlyTest, GenericCRUDTest, LoginRequiredGETOnlyTest, LoginRequiredCRUDTest, LoginRequiredTest, ManualTest, checkMatch, checkMatchDB
from http.cookies import SimpleCookie

django.setup()
serverUrl = TestGenericInterfaces.getHost()

# ---------------------- UNIT TEST FOR BASIC CRUD OPERATIONS -------------

# test for API end point /parties with party type user
# TODO: test for party type staff, admin as well
class UserPartyCRUDTest(LoginRequiredCRUDTest, TestCase):
    sample = UserPartySample(serverUrl)

    def test_for_get_all(self):
        # get all by type
        url = self.getUrl(self.sample.url, 'partyType', self.sample.PARTY_TYPE_USER)
        self.getAllHelper(url, 'partyId', self.credentialId)

# test for API end point /parties with party type organization 
# TODO: test for party type consortium
class OrganizationPartyCRUDTest(LoginRequiredCRUDTest, TestCase):
    sample = OrganizationPartySample(serverUrl)
    countrySample = CountrySample(serverUrl)

    def setUp(self):
        super(OrganizationPartyCRUDTest,self).setUp()
        countryId = self.countrySample.forcePost(self.countrySample.data)
        self.sample.data['country']=self.sample.updateData['country']=countryId

    def test_for_get_all(self):
        # get all by type
        url = self.getUrl(self.sample.url, 'partyType', self.sample.PARTY_TYPE_ORG)
        self.getAllHelper(url)

# test for API end point /parties/countries
class CountryGETOnlyTest(GenericGETOnlyTest, TestCase):
    sample = CountrySample(serverUrl)

    # only method is test_for_get_all
    def test_for_get(self):
        pass

# test for API end point /parties/ipranges/
class IpRangeCRUDTest(LoginRequiredCRUDTest, TestCase):
    sample = IpRangeSample(serverUrl)
    partySample = OrganizationPartySample(serverUrl)
    countrySample = CountrySample(serverUrl)
    partyId = None

    def setUp(self):
        super(IpRangeCRUDTest,self).setUp()
        countryId = self.countrySample.forcePost(self.countrySample.data)
        self.partySample.data['country']=countryId
        self.partyId = self.partySample.forcePost(self.partySample.data)
        self.sample.data['partyId']=self.sample.updateData['partyId']=self.partyId
        self.sample.invalidData_oversize['partyId'] = self.partyId
        self.sample.invalidData_private['partyId'] = self.partyId

    def test_for_update_private_ipRange(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = self.getUrl(sample.url, sample.pkName, pk)
        if self.apiKey:
            self.client.cookies = SimpleCookie({'apiKey':self.apiKey})

        # the default content type for put is 'application/octet-stream'
        res = self.client.put(url, json.dumps(sample.invalidData_private), content_type='application/json')

        self.assertEqual(res.status_code, 400)
        is_private = json.loads(res.content)['IP Range'] == sample.getPrivateRangeIPErrorMessage()
        self.assertTrue(is_private, 'Private_IpRange_Test_for_Update: Expected \
                                     IpRange to have a private IP address, but failed.')

    def test_for_update_oversize_ipRange(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = self.getUrl(sample.url, sample.pkName, pk)
        if self.apiKey:
            self.client.cookies = SimpleCookie({'apiKey':self.apiKey})

        # the default content type for put is 'application/octet-stream'
        res = self.client.put(url, json.dumps(sample.invalidData_oversize), content_type='application/json')

        self.assertEqual(res.status_code, 400)
        is_oversize = json.loads(res.content)['IP Range'] == sample.getOutRangeIPErrorMessage()
        self.assertTrue(is_oversize, 'Oversize_IpRange_Test_for_Update: Expected \
                                     IpRange to be out of range, but failed.')

    def test_for_create_private_ipRange(self):
        sample = self.sample
        url = self.getUrl(sample.url)
        if self.apiKey:
            self.client.cookies = SimpleCookie({'apikey': self.apiKey})

        res = self.client.post(url, sample.invalidData_private)

        self.assertEqual(res.status_code, 400)
        is_private = json.loads(res.content)['IP Range'] == sample.getPrivateRangeIPErrorMessage()
        self.assertTrue(is_private, 'Private_IpRange_Test_for_Create: Expected \
                                     IpRange to have a private IP address, but failed.')

    def test_for_create_oversize_ipRange(self):
        sample = self.sample
        url = self.getUrl(sample.url)
        if self.apiKey:
            self.client.cookies = SimpleCookie({'apikey': self.apiKey})

        res = self.client.post(url, sample.invalidData_oversize)

        self.assertEqual(res.status_code, 400)
        is_oversize = json.loads(res.content)['IP Range'] == sample.getOutRangeIPErrorMessage()
        self.assertTrue(is_oversize, 'Oversize_IpRange_Test_for_Create: Expected \
                                      IpRange to be out of range, but failed.')

    def test_for_get(self):
        pass

    def getUrl(self, url, pkName = None, pk = None):
        # need partyId for filter
        fullUrl = super(IpRangeCRUDTest,self).getUrl(url, pkName, pk) + '&%s=%s' % ('partyId', self.partyId)
        return fullUrl

# test for API end point /parties/consortiums/
# returns consortium info and associated credential info
class ConsortiumPartyCRUDTest(LoginRequiredCRUDTest, TestCase):
    sample = ConsortiumPartySample(serverUrl)
    partnerId = None

    def setUp(self):
        super(ConsortiumPartyCRUDTest,self).setUp()

        countrySample = CountrySample(serverUrl)
        countryId = countrySample.forcePost(countrySample.data)
        self.sample.data['country']=self.sample.updateData['country']=countryId   

        partnerSample = PartnerSample(serverUrl)
        self.partnerId = partnerSample.forcePost(partnerSample.data)


    def test_for_get(self):
        sample = self.sample
        # note this should not override the parent credential sample used for login 
        # so use a different name
        consortiumCredentialSample = self.initForcePostConsortiumCredentialSample(serverUrl)
        pk = self.forcePostConsortiumItem(consortiumCredentialSample)

        url = self.getUrl(sample.url, sample.pkName, pk) 
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

        resObj = json.loads(res.content)
        self.assertConsortiumItem(sample.data, consortiumCredentialSample.data, consortiumCredentialSample, resObj, sample.pkName, pk)
        self.assertEqual(resObj[0]['hasIpRange'], False)

        # test for case where ip range is associated
        ipRangeSample = IpRangeSample(serverUrl)
        ipRangeSample.data['partyId'] = pk
        ipRangeSample.forcePost(ipRangeSample.data)

        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

        resObj = json.loads(res.content)
        self.assertEqual(resObj[0]['hasIpRange'], True)

    # testcase 5 : throw error & does not save when credential serializer failed
    def test_for_put_case5(self):
        # create new consortium party and get partyId "pk"
        sample = self.sample
        pk = sample.forcePost(sample.data)

        # initialize data from credentialSample
        consortiumCredentialSample = CredentialSample(serverUrl)
        consortiumCredentialSample.updateData_invalid['partnerId'] = self.partnerId
        consortiumCredentialSample.data['partnerId'] = self.partnerId
        consortiumCredentialSample.data['partyId'] = pk
        consortiumCredentialSample.updateData_invalid['partyId'] = pk

        # construct credential on Database
        consortiumCredentialSample.forcePost(consortiumCredentialSample.data)

        # combine updateData from partySample and invalid updateData from CredentialSample into one data "putData"
        putData = self.composeConsortiumPostData(sample.updateData, consortiumCredentialSample.updateData_invalid)
        url = self.getUrl(sample.url, sample.pkName, pk)

        # pushing putData into Database
        res = self.client.put(url, json.dumps(putData), content_type='application/json')

        # test failing to push into the database
        self.assertEqual(res.status_code, 400)
        # test data from party on Database == sample.data
        self.assertEqual(checkMatchDB(sample.data, sample.model, sample.pkName, pk), True)

        # hashing the password and test data from credential on Database == consortiumCredentialSample.data
        consortiumCredentialSample.data['password'] = consortiumCredentialSample.hashPassword(consortiumCredentialSample.data['password'])
        self.assertEqual(checkMatchDB(consortiumCredentialSample.data, consortiumCredentialSample.model, sample.pkName, pk), True)

    # testcase 4 : throw error & does not save when party serializer failed
    def test_for_put_case4(self):
        # create new consortium party and get partyId "pk"
        sample = self.sample
        pk = sample.forcePost(sample.data)

        # initialize data from credentialSample
        consortiumCredentialSample = CredentialSample(serverUrl)
        consortiumCredentialSample.updateData['partnerId'] = self.partnerId
        consortiumCredentialSample.data['partnerId'] = self.partnerId
        consortiumCredentialSample.data['partyId'] = pk
        consortiumCredentialSample.updateData['partyId'] = pk

        # construct credential on Database
        consortiumCredentialSample.forcePost(consortiumCredentialSample.data)

        # combine invalid updateData from partySample and updateData from CredentialSample into one data "putData"
        putData = self.composeConsortiumPostData(sample.updateData_invalid, consortiumCredentialSample.updateData)
        url = self.getUrl(sample.url, sample.pkName, pk)

        # pushing putData into Database
        res = self.client.put(url, json.dumps(putData), content_type='application/json')

        # test failing to push into the database
        self.assertEqual(res.status_code, 400)
        # test data from party on Database == sample.data
        self.assertEqual(checkMatchDB(sample.data, sample.model, sample.pkName, pk), True)

        # hashing the password and test data from credential on Database == consortiumCredentialSample.data
        consortiumCredentialSample.data['password'] = consortiumCredentialSample.hashPassword(consortiumCredentialSample.data['password'])
        self.assertEqual(checkMatchDB(consortiumCredentialSample.data, consortiumCredentialSample.model, sample.pkName, pk), True)

    # testcase 3: update party only
    def test_for_put_case3(self):
        # create new consortium party and get partyId "pk"
        sample = self.sample
        pk = sample.forcePost(sample.data)

        # set putData to exclude update data from credential
        putData = copy.deepcopy(sample.updateData)
        putData['partyId'] = pk

        url = self.getUrl(sample.url, sample.pkName, pk)

        # pushing putData into Database
        res = self.client.put(url, json.dumps(putData), content_type='application/json')

        # test pushing successfully into the database
        self.assertEqual(res.status_code, 200)
        # test party data from the database = party sample's updateData
        self.assertEqual(checkMatchDB(sample.updateData, sample.model, sample.pkName, pk), True)

    # testcase 2: throw error if credential not exist & username/pwd not exist
    def test_for_put_case2(self):
        # create new consortium party and get partyId "pk"
        sample = self.sample
        pk = sample.forcePost(sample.data)

        # initialize data from credentialSample
        consortiumCredentialSample = CredentialSample(serverUrl)
        consortiumCredentialSample.updateData_no_pwd['partnerId'] = self.partnerId
        consortiumCredentialSample.updateData_no_pwd['partyId'] = pk

        # combine updateData from partySample and updateData w/o pwd from CredentialSample into one data "putData"
        putData = self.composeConsortiumPostData(sample.updateData, consortiumCredentialSample.updateData_no_pwd)
        url = self.getUrl(sample.url, sample.pkName, pk)

        # pushing putData into Database
        res = self.client.put(url, json.dumps(putData), content_type='application/json')

        # test failing to push into the database
        self.assertEqual(res.status_code, 400)
        # test party data from the database = party sample's data
        self.assertEqual(checkMatchDB(sample.data, sample.model, sample.pkName, pk), True)
        # test credential does not exist
        self.assertEqual(checkMatchDB(None, consortiumCredentialSample.model, sample.pkName, pk), True)

    # testcase 1: create credential when no exist
    def test_for_put_case1(self):
        # create new consortium party and get partyId "pk"
        sample = self.sample
        pk = sample.forcePost(sample.data)

        # initialize data from credentialSample
        consortiumCredentialSample = CredentialSample(serverUrl)
        consortiumCredentialSample.updateData['partnerId'] = self.partnerId
        consortiumCredentialSample.data['partyId'] = pk
        consortiumCredentialSample.updateData['partyId'] = pk

        # combine two updateData from partySample and CredentialSample into one data "putData"
        putData = self.composeConsortiumPostData(sample.updateData, consortiumCredentialSample.updateData)
        url = self.getUrl(sample.url, sample.pkName, pk)

        # pushing putData into Database
        res = self.client.put(url, json.dumps(putData), content_type='application/json')

        # test pushing successfully into the database
        self.assertEqual(res.status_code, 200)
        # test if party data from the database = party sample's updateData
        self.assertEqual(checkMatchDB(sample.updateData, sample.model, sample.pkName, pk), True)

        # hashing the password and test data from credential on Database == consortiumCredentialSample.updateData
        consortiumCredentialSample.updateData['password'] = consortiumCredentialSample.hashPassword(consortiumCredentialSample.updateData['password'])
        self.assertEqual(checkMatchDB(consortiumCredentialSample.updateData, consortiumCredentialSample.model, sample.pkName, pk), True)

    def test_for_get_all(self):
        pass

    # API end point requires to create consortium and its user together
    def test_for_create(self):
        sample = self.sample
        consortiumCredentialSample = CredentialSample(serverUrl)
        consortiumCredentialSample.data['partnerId'] = self.partnerId
        postData = self.composeConsortiumPostData(sample.data, consortiumCredentialSample.data)

        url = self.getUrl(sample.url)
        res = self.client.post(url, postData)

        self.assertEqual(res.status_code, 201)
        resObj = json.loads(res.content)
        pk = resObj[0][sample.pkName]
        # manipulate sample data to match the test condition
        consortiumCredentialSample.data['partyId'] = pk
        self.assertConsortiumItem(sample.data, consortiumCredentialSample.data, consortiumCredentialSample, resObj, sample.pkName, pk)

    def test_for_update(self):
        sample = self.sample
        consortiumCredentialSample = self.initForcePostConsortiumCredentialSample(serverUrl)
        pk = self.forcePostConsortiumItem(consortiumCredentialSample)

        # create put data with both party update data and credential update data
        putData = self.composeConsortiumPostData(sample.updateData, consortiumCredentialSample.updateData)

        url = self.getUrl(sample.url, sample.pkName, pk)

        # the default content type for put is 'application/octet-stream'
        res = self.client.put(url, json.dumps(putData), content_type='application/json')

        self.assertEqual(res.status_code, 200)
        resObj = json.loads(res.content)
        # manipulate sample update data to match the test condition
        self.assertConsortiumItem(sample.updateData, consortiumCredentialSample.updateData, consortiumCredentialSample, resObj, sample.pkName, pk)

    def initForcePostConsortiumCredentialSample(self, serverUrl):
        consortiumCredentialSample = CredentialSample(serverUrl)

        consortiumCredentialSample.data['partnerId'] = consortiumCredentialSample.updateData['partnerId'] = self.partnerId
        return consortiumCredentialSample

    # alternative method is to post data by call create API
    def forcePostConsortiumItem(self, consortiumCredentialSample):
        sample = self.sample
        pk = sample.forcePost(sample.data)

        consortiumCredentialSample.data['partyId'] = consortiumCredentialSample.updateData['partyId'] = pk
        consortiumCredentialSample.forcePost(consortiumCredentialSample.data)

        return pk

    # create post/put data with both consortium data and credential data
    def composeConsortiumPostData(self, consortiumSampleData, consortiumCredentialSampleData):
        postData = copy.deepcopy(consortiumSampleData)

        for key in consortiumCredentialSampleData:
            if consortiumCredentialSampleData[key] is not None:
                postData[key] = consortiumCredentialSampleData[key]

        return postData

    def assertConsortiumItem(self, consortiumSampleData, consortiumCredentialSampleData, consortiumCredentialSample, resObj, pkName, pk):
        self.assertEqual(checkMatch(consortiumSampleData, resObj[0], pkName, pk), True)
        self.assertEqual(checkMatchDB(consortiumSampleData, self.sample.model, pkName, pk), True)
        # manipulate sample data to match the test condition
        consortiumCredentialSampleData['password'] = consortiumCredentialSample.hashPassword(consortiumCredentialSampleData['password'])
        self.assertEqual(checkMatch(consortiumCredentialSampleData, resObj[1], pkName, pk), True)
        self.assertEqual(checkMatchDB(consortiumCredentialSampleData, consortiumCredentialSample.model, pkName, pk), True)

# test for API end point /parties/institutions/
# returns organization info and associated credential info
# difference between this API and /parties API is this API will include 
# affliated consortium info and credential info
class InstitutionPartyCRUDTest(LoginRequiredCRUDTest, TestCase):
    sample = InstitutionPartySample(serverUrl)
    partnerId = None
    consortiumPartyId = None

    def setUp(self):
        super(InstitutionPartyCRUDTest,self).setUp()
        consortiumSample = ConsortiumPartySample(serverUrl)

        countrySample = CountrySample(serverUrl)
        countryId = countrySample.forcePost(countrySample.data)
        self.sample.data['country']=self.sample.updateData['country']=countryId   
        consortiumSample.data['country']=countryId   

        partnerSample = PartnerSample(serverUrl)
        self.partnerId = partnerSample.forcePost(partnerSample.data)

        self.consortiumPartyId = consortiumSample.forcePost(consortiumSample.data)

    def test_for_get(self):
        sample = self.sample
        # note this should not override the parent credential sample used for login 
        # so use a different name
        institutionCredentialSample = self.initForcePostInstitutionCredentialSample(serverUrl)
        pk = self.forcePostInstitutionItem(institutionCredentialSample)

        url = self.getUrl(sample.url, sample.pkName, pk) 
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

        resObj = json.loads(res.content)
        self.assertInstitutionItem(sample.data, institutionCredentialSample.data, institutionCredentialSample, resObj, sample.pkName, pk)
        self.assertEqual(resObj[0]['hasIpRange'], False)
        self.assertEqual(resObj[0]['consortiums'][0], self.consortiumPartyId)

        # test for case where ip range is associated
        ipRangeSample = IpRangeSample(serverUrl)
        ipRangeSample.data['partyId'] = pk
        ipRangeSample.forcePost(ipRangeSample.data)

        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

        resObj = json.loads(res.content)
        self.assertEqual(resObj[0]['hasIpRange'], True)

    # testcase 5 : throw error & does not save when credential serializer failed
    def test_for_put_case5(self):
        # create new consortium party and get partyId "pk"
        sample = self.sample
        pk = sample.forcePost(sample.data)

        # initialize data from credentialSample
        institutionCredentialSample = CredentialSample(serverUrl)
        institutionCredentialSample.updateData_invalid['partnerId'] = self.partnerId
        institutionCredentialSample.data['partnerId'] = self.partnerId
        institutionCredentialSample.data['partyId'] = pk
        institutionCredentialSample.updateData_invalid['partyId'] = pk

        # construct credential on Database
        institutionCredentialSample.forcePost(institutionCredentialSample.data)

        # combine updateData from partySample and invalid updateData from CredentialSample into one data "putData"
        putData = self.composeInstitutionPostData(sample.updateData, institutionCredentialSample.updateData_invalid)
        url = self.getUrl(sample.url, sample.pkName, pk)

        # pushing putData into Database
        res = self.client.put(url, json.dumps(putData), content_type='application/json')

        # test failing to push into the database
        self.assertEqual(res.status_code, 400)
        # test data from party on Database == sample.data
        self.assertEqual(checkMatchDB(sample.data, sample.model, sample.pkName, pk), True)

        # hashing the password and test data from credential on Database == institutionCredentialSample.data
        institutionCredentialSample.data['password'] = institutionCredentialSample.hashPassword(institutionCredentialSample.data['password'])
        self.assertEqual(checkMatchDB(institutionCredentialSample.data, institutionCredentialSample.model, sample.pkName, pk), True)

    # testcase 4 : throw error & does not save when party serializer failed
    def test_for_put_case4(self):
        # create new consortium party and get partyId "pk"
        sample = self.sample
        pk = sample.forcePost(sample.data)

        # initialize data from credentialSample
        institutionCredentialSample = CredentialSample(serverUrl)
        institutionCredentialSample.updateData['partnerId'] = self.partnerId
        institutionCredentialSample.data['partnerId'] = self.partnerId
        institutionCredentialSample.data['partyId'] = pk
        institutionCredentialSample.updateData['partyId'] = pk

        # construct credential on Database
        institutionCredentialSample.forcePost(institutionCredentialSample.data)

        # combine invalid updateData from partySample and updateData from CredentialSample into one data "putData"
        putData = self.composeInstitutionPostData(sample.updateData_invalid, institutionCredentialSample.updateData)
        url = self.getUrl(sample.url, sample.pkName, pk)

        # pushing putData into Database
        res = self.client.put(url, json.dumps(putData), content_type='application/json')

        # test failing to push into the database
        self.assertEqual(res.status_code, 400)
        # test data from party on Database == sample.data
        self.assertEqual(checkMatchDB(sample.data, sample.model, sample.pkName, pk), True)

        # hashing the password and test data from credential on Database == institutionCredentialSample.data
        institutionCredentialSample.data['password'] = institutionCredentialSample.hashPassword(institutionCredentialSample.data['password'])
        self.assertEqual(checkMatchDB(institutionCredentialSample.data, institutionCredentialSample.model, sample.pkName, pk), True)

    # testcase 3: update party only
    def test_for_put_case3(self):
        # create new consortium party and get partyId "pk"
        sample = self.sample
        pk = sample.forcePost(sample.data)

        # set putData to exclude update data from credential
        putData = copy.deepcopy(sample.updateData)
        putData['partyId'] = pk

        url = self.getUrl(sample.url, sample.pkName, pk)

        # pushing putData into Database
        res = self.client.put(url, json.dumps(putData), content_type='application/json')

        # test pushing successfully into the database
        self.assertEqual(res.status_code, 200)
        # test party data from the database = party sample's updateData
        self.assertEqual(checkMatchDB(sample.updateData, sample.model, sample.pkName, pk), True)

    # testcase 2: throw error if credential not exist & username/pwd not exist
    def test_for_put_case2(self):
        # create new consortium party and get partyId "pk"
        sample = self.sample
        pk = sample.forcePost(sample.data)

        # initialize data from credentialSample
        institutionCredentialSample = CredentialSample(serverUrl)
        institutionCredentialSample.updateData_no_pwd['partnerId'] = self.partnerId
        institutionCredentialSample.updateData_no_pwd['partyId'] = pk

        # combine updateData from partySample and updateData w/o pwd from CredentialSample into one data "putData"
        putData = self.composeInstitutionPostData(sample.updateData, institutionCredentialSample.updateData_no_pwd)
        url = self.getUrl(sample.url, sample.pkName, pk)

        # pushing putData into Database
        res = self.client.put(url, json.dumps(putData), content_type='application/json')

        # test failing to push into the database
        self.assertEqual(res.status_code, 400)
        # test party data from the database = party sample's data
        self.assertEqual(checkMatchDB(sample.data, sample.model, sample.pkName, pk), True)
        # test credential does not exist
        self.assertEqual(checkMatchDB(None, institutionCredentialSample.model, sample.pkName, pk), True)

    # testcase 1: create credential when no exist
    def test_for_put_case1(self):
        # create new consortium party and get partyId "pk"
        sample = self.sample
        pk = sample.forcePost(sample.data)

        # initialize data from credentialSample
        institutionCredentialSample = CredentialSample(serverUrl)
        institutionCredentialSample.updateData['partnerId'] = self.partnerId
        institutionCredentialSample.data['partyId'] = pk
        institutionCredentialSample.updateData['partyId'] = pk

        # combine two updateData from partySample and CredentialSample into one data "putData"
        putData = self.composeInstitutionPostData(sample.updateData, institutionCredentialSample.updateData)
        url = self.getUrl(sample.url, sample.pkName, pk)

        # pushing putData into Database
        res = self.client.put(url, json.dumps(putData), content_type='application/json')

        # test pushing successfully into the database
        self.assertEqual(res.status_code, 200)
        # test if party data from the database = party sample's updateData
        self.assertEqual(checkMatchDB(sample.updateData, sample.model, sample.pkName, pk), True)

        # hashing the password and test data from credential on Database == institutionCredentialSample.updateData
        institutionCredentialSample.updateData['password'] = institutionCredentialSample.hashPassword(institutionCredentialSample.updateData['password'])
        self.assertEqual(checkMatchDB(institutionCredentialSample.updateData, institutionCredentialSample.model, sample.pkName, pk), True)

    def test_for_get_all(self):
        pass

    # API end point requires to create consortium and its user together
    def test_for_create(self):
        sample = self.sample
        institutionCredentialSample = CredentialSample(serverUrl)
        institutionCredentialSample.data['partnerId'] = self.partnerId
        postData = self.composeInstitutionPostData(sample.data, institutionCredentialSample.data)

        url = self.getUrl(sample.url)
        res = self.client.post(url, postData)

        self.assertEqual(res.status_code, 201)
        resObj = json.loads(res.content)
        pk = resObj[0][sample.pkName]
        # manipulate sample data to match the test condition
        institutionCredentialSample.data['partyId'] = pk
        self.assertInstitutionItem(sample.data, institutionCredentialSample.data, institutionCredentialSample, resObj, sample.pkName, pk)

    def test_for_update(self):
        sample = self.sample
        institutionCredentialSample = self.initForcePostInstitutionCredentialSample(serverUrl)
        pk = self.forcePostInstitutionItem(institutionCredentialSample)

        # create put data with both party update data and credential update data
        putData = self.composeInstitutionPostData(sample.updateData, institutionCredentialSample.updateData)

        url = self.getUrl(sample.url, sample.pkName, pk)

        # the default content type for put is 'application/octet-stream'
        res = self.client.put(url, json.dumps(putData), content_type='application/json')

        self.assertEqual(res.status_code, 200)
        resObj = json.loads(res.content)
        self.assertInstitutionItem(sample.updateData, institutionCredentialSample.updateData, institutionCredentialSample, resObj, sample.pkName, pk)

    def initForcePostInstitutionCredentialSample(self, serverUrl):
        institutionCredentialSample = CredentialSample(serverUrl)

        institutionCredentialSample.data['partnerId'] = institutionCredentialSample.updateData['partnerId'] = self.partnerId

        return institutionCredentialSample

    # alternative method is to post data by call create API
    def forcePostInstitutionItem(self, institutionCredentialSample):
        sample = self.sample
        pk = sample.forcePost(sample.data)

        institutionCredentialSample.data['partyId'] = institutionCredentialSample.updateData['partyId'] = pk
        institutionCredentialSample.forcePost(institutionCredentialSample.data)

        partyAffiliationSample = PartyAffiliationSample(serverUrl)
        partyAffiliationSample.setParentId(self.consortiumPartyId)
        partyAffiliationSample.setChildId(pk)
        partyAffiliationSample.forcePost(partyAffiliationSample.data)

        return pk

    # create post/put data with both consortium data and credential data
    def composeInstitutionPostData(self, institutionSampleData, institutionCredentialSampleData):
        postData = copy.deepcopy(institutionSampleData)

        for key in institutionCredentialSampleData:
            if institutionCredentialSampleData[key] is not None:
                postData[key] = institutionCredentialSampleData[key]

        return postData

    def assertInstitutionItem(self, institutionSampleData, institutionCredentialSampleData, institutionCredentialSample, resObj, pkName, pk):
        self.assertEqual(checkMatch(institutionSampleData, resObj[0], pkName, pk), True)
        self.assertEqual(checkMatchDB(institutionSampleData, self.sample.model, pkName, pk), True)

        # manipulate sample data to match the test condition
        institutionCredentialSampleData['password'] = institutionCredentialSample.hashPassword(institutionCredentialSampleData['password'])
        self.assertEqual(checkMatch(institutionCredentialSampleData, resObj[1], pkName, pk), True)
        self.assertEqual(checkMatchDB(institutionCredentialSampleData, institutionCredentialSample.model, pkName, pk), True)

# test for end point /parties/affiliations/
# get_all and update methods unavailable, all available methods need to be override
# so no need to inherit from LoginRequiredCRUDTest
class PartyAffiliationCRUDTest(LoginRequiredTest, TestCase):
    sample = PartyAffiliationSample(serverUrl)
    parentPartySample = ConsortiumPartySample(serverUrl)
    childPartySample = InstitutionPartySample(serverUrl)

    def setUp(self):
        super(PartyAffiliationCRUDTest,self).setUp()

        countrySample = CountrySample(serverUrl)
        countryId = countrySample.forcePost(countrySample.data)
        self.parentPartySample.data['country']=self.childPartySample.data['country']=countryId  

        parentPartyId = self.parentPartySample.forcePost(self.parentPartySample.data) 
        childPartyId = self.childPartySample.forcePost(self.childPartySample.data) 

        self.sample.setParentId(parentPartyId)
        self.sample.setChildId(childPartyId)

    def test_for_get(self):
        sample = self.sample
        sample.forcePost(sample.data)

        parentPartyId = sample.getParentId()
        parentPartyType = self.parentPartySample.getPartyType()

        childPartyId = sample.getChildId()
        childPartyType = self.childPartySample.getPartyType()

        # get by consortium (parent organization)
        url = self.getUrl(sample.url) 
        url = '%s&partyId=%s&partyType=%s' % (url, parentPartyId, parentPartyType)

        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        resObj = json.loads(res.content)
        self.assertEqual(checkMatch(self.childPartySample.data, resObj, 'partyId', childPartyId), True)
        self.assertEqual(resObj[0]['consortiums'][0], parentPartyId)

        # get by institution (child organization)
        url = self.getUrl(sample.url) 
        url = '%s&partyId=%s&partyType=%s' % (url, childPartyId, childPartyType)

        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(checkMatch(self.parentPartySample.data, json.loads(res.content), 'partyId', parentPartyId), True)

    def test_for_create(self):
        sample = self.sample
        parentPartyId = sample.getParentId()
        childPartyId = sample.getChildId()

        url = self.getUrl(sample.url) 
        url = '%s&parentPartyId=%s&childPartyId=%s' % (url, parentPartyId, childPartyId)

        res = self.client.post(url, sample.data)

        self.assertEqual(res.status_code, 201)
        # return content is child organization data
        # resObj = json.loads(res.content)
        # self.assertEqual(checkMatch(self.childPartySample.data, resObj, 'partyId', childPartyId), True)
        # self.assertEqual(resObj['consortiums'][0], parentPartyId)
        self.assertIsNotNone(TestGenericInterfaces.forceGet(sample.model,'parentPartyId',parentPartyId))
        self.assertIsNotNone(TestGenericInterfaces.forceGet(sample.model,'childPartyId',childPartyId))

    def test_for_delete(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)

        parentPartyId = sample.getParentId()
        childPartyId = sample.getChildId()

        url = self.getUrl(sample.url) 
        url = '%s&parentPartyId=%s&childPartyId=%s' % (url, parentPartyId, childPartyId)

        res = self.client.delete(url)

        self.assertIsNone(TestGenericInterfaces.forceGet(sample.model,sample.pkName,pk))

# ----------------- END OF BASIC CRUD OPERATIONS ----------------------

# test for API end point /parties/org/
# get organization by ip
class GetOrgByIpTest(TestCase):
    sample = IpRangeSample(serverUrl)
    partySample = OrganizationPartySample(serverUrl)
    countrySample = CountrySample(serverUrl)
    url = None

    def setUp(self):
        countryId = self.countrySample.forcePost(self.countrySample.data)
        self.partySample.data['country']=countryId
        self.partyId = self.partySample.forcePost(self.partySample.data)
        self.sample.data['partyId']=self.sample.updateData['partyId']=self.partyId
        self.sample.forcePost(self.sample.data)
        self.url = serverUrl + 'parties/org/?ip=%s' % self.sample.getInRangeIp()

    def test_for_get_by_ip(self):
        res = self.client.get(self.url)

        self.assertEqual(res.status_code, 200)
        # The raw response will be bytes so need to convert to string and then compare
        self.assertEqual(res.content.decode(), self.partySample.getName())

# test for API end point /parties/orgstatus/
# get organization and its subscription status to partner by ip
class GetOrgAndSubStatusTest(TestCase):
    sample = IpRangeSample(serverUrl)
    partnerSample = PartnerSample(serverUrl)
    partySample = OrganizationPartySample(serverUrl)
    countrySample = CountrySample(serverUrl)
    subscriptionSample = SubscriptionSample(serverUrl)
    url = None
    partnerId = None
    partyId = None

    def setUp(self):
        self.partnerId = self.partnerSample.forcePost(self.partnerSample.data)
        countryId = self.countrySample.forcePost(self.countrySample.data)
        self.partySample.data['country']=countryId
        self.partyId = self.partySample.forcePost(self.partySample.data)
        self.sample.data['partyId']=self.partyId
        self.sample.forcePost(self.sample.data)
        self.url = serverUrl + 'parties/orgstatus/?ip=%s&partnerId=%s' % (self.sample.getInRangeIp(), self.partnerId)

    def test_for_unsubscribed(self):
        res = self.client.get(self.url)

        self.assertEqual(res.status_code, 200)
        resObj = json.loads(res.content)
        self.assertEqual(resObj['name'], self.partySample.getName())
        self.assertEqual(resObj['status'], 'not subscribed')

    def test_for_subscribed(self):
        self.subscriptionSample.setPartnerId(self.partnerId)
        self.subscriptionSample.setPartyId(self.partyId)
        self.subscriptionSample.forcePost(self.subscriptionSample.data)

        res = self.client.get(self.url)

        self.assertEqual(res.status_code, 200)
        resObj = json.loads(res.content)
        self.assertEqual(resObj['name'], self.partySample.getName())
        self.assertEqual(resObj['status'], 'subscribed')

# test for API end point /parties/organizations/
# get subscribed organization list by partner
class GetSubOrgListByPartnerTest(TestCase):
    sample = IpRangeSample(serverUrl)
    partnerSample = PartnerSample(serverUrl)
    partySample = OrganizationPartySample(serverUrl)
    countrySample = CountrySample(serverUrl)
    subscriptionSample = SubscriptionSample(serverUrl)
    url = None

    def setUp(self):
        partnerId = self.partnerSample.forcePost(self.partnerSample.data)

        countryId = self.countrySample.forcePost(self.countrySample.data)

        self.partySample.data['country']=countryId
        partyId = self.partySample.forcePost(self.partySample.data)

        self.sample.data['partyId']=partyId
        self.sample.forcePost(self.sample.data)

        self.subscriptionSample.setPartnerId(partnerId)
        self.subscriptionSample.setPartyId(partyId)
        self.subscriptionSample.forcePost(self.subscriptionSample.data)

        self.url = serverUrl + 'parties/organizations/?partnerId=%s' % partnerId

    def test_for_list(self):
        res = self.client.get(self.url)

        self.assertEqual(res.status_code, 200)
        resObj = json.loads(res.content)[0]
        self.assertEqual(resObj[0], self.partySample.getName())
        self.assertEqual(resObj[1], self.countrySample.getName())

# test for API end point /parties/usage/
# test in manualTests.py
# deprecated and replaced by POL functions
# class GetUsageRequestTest(ManualTest, TestCase):
#     path = "/parties/usage/"
#     testMethodStr = "running ./manage.py test party.manualTests (the UI invocation from librarians is not public yet)"

# test for API end point /parties/consortiuminstitutions/{consortiumId}
# this endpoint is not working

print("Running unit tests on party web services API.........")

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
