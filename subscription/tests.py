#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys
import json
import copy
from django.test import TestCase
from subscription.models import Subscription, SubscriptionTransaction, ActivationCode
from .testSamples import SubscriptionSample, SubscriptionTransactionSample, ActivationCodeSample
from party.testSamples import UserPartySample, CountrySample, OrganizationPartySample, IpRangeSample, ConsortiumPartySample, InstitutionPartySample, PartyAffiliationSample, ImageInfoSample
from partner.testSamples import PartnerSample, SubscriptionTermSample
from authentication.testSamples import CredentialSample
from common.tests import TestGenericInterfaces, GenericCRUDTest, GenericTest, LoginRequiredTest, ManualTest, checkMatch, checkMatchDB
from rest_framework import status
from .controls import PaymentControl
from http.cookies import SimpleCookie

# Create your tests here.                                                                                                                                                                                 
django.setup()
serverUrl = TestGenericInterfaces.getHost()

# ---------------------- UNIT TEST FOR BASIC CRUD OPERATIONS -------------

# test for API end point /subscriptions/
# except for GET that is explicitly override in end point, all other actions
# (UPDATE and DELETE) queries item by party id instead of subscription id
class SubscriptionCRUDTest(LoginRequiredTest, TestCase):
    partyId = None
    partnerId = None
    sample = SubscriptionSample(serverUrl)

    def setUp(self):
        super(SubscriptionCRUDTest,self).setUp()

        partnerSample = PartnerSample(serverUrl)
        self.partnerId = partnerSample.forcePost(partnerSample.data)

        partySample = UserPartySample(serverUrl)
        self.partyId = partySample.forcePost(partySample.data)

        self.sample.data['partyId']=self.sample.updateData['partyId']=self.partyId
        self.sample.data['partnerId']=self.sample.updateData['partnerId']=self.partnerId

    # post request for subscription is not generic. It creates a SubscriptionTransaction
    # object in addition to a Subscription object.
    # creation via basic CRUD format
    # Need valid phoenix credential
    # Potential API end point threat: no role based authorization
    def test_for_create(self):
        sample = self.sample
        url = self.getUrl(sample.url)

        res = self.client.post(url, sample.data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        resObj = json.loads(res.content)
        self.assertEqual(checkMatchDB(sample.data, sample.model,sample.pkName,resObj[sample.pkName]), True)
        transactionId = resObj['subscriptionTransactionId']
        self.assertIsNotNone(TestGenericInterfaces.forceGet(SubscriptionTransaction,'subscriptionTransactionId',transactionId))

    # create subscription by activation code
    def test_for_create_by_activation(self):
        sample = self.sample
        # no need for user credential
        url = sample.url

        activationCodeSample = ActivationCodeSample(serverUrl)
        activationCodeSample.initTransctionType()
        activationCodeSample.setPartnerId(self.partnerId)
        activationCodeSample.forcePost(activationCodeSample.data)

        activationCode = activationCodeSample.getActivationCode()
        data ={"partyId":self.partyId, "activationCode":activationCode}
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        resObj = json.loads(res.content)
        self.assertIsNotNone(TestGenericInterfaces.forceGet(sample.model,sample.pkName,resObj[sample.pkName]))
        transactionId = resObj['subscriptionTransactionId']
        self.assertIsNotNone(TestGenericInterfaces.forceGet(SubscriptionTransaction,'subscriptionTransactionId',transactionId))

    # get by subscriptionId, partyId or userIdentifier
    def test_for_get(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)

        # get by subscriptionId
        url = self.getUrl(sample.url, sample.pkName, pk) 
        self.runGetTestByIdentifier(url, pk)

        # get by partyId
        url = self.getUrl(sample.url, 'partyId', self.partyId) 
        self.runGetTestByIdentifier(url, pk)

        # get by userIdentifier
        credentialSample = CredentialSample(serverUrl)
        credentialSample.setPartyId(self.partyId)
        credentialSample.setPartnerId(self.partnerId)
        credentialSample.forcePost(credentialSample.data)

        url = self.getUrl(sample.url, 'userIdentifier', credentialSample.getUserIdentifier())
        # need to pass ipAddress as arg even when not needed
        url = '%s&partnerId=%s&ipAddress=' % (url, self.partnerId)
        self.runGetTestByIdentifier(url, pk)

    # get by ipAddress
    def test_for_get_by_ip_address(self):
        # override party setup
        countrySample = CountrySample(serverUrl)
        countryId = countrySample.forcePost(countrySample.data)

        partySample = OrganizationPartySample(serverUrl)
        partySample.setCountry(countryId)
        self.partyId = partySample.forcePost(partySample.data)

        ipRangeSample = IpRangeSample(serverUrl)
        ipRangeSample.setPartyId(self.partyId)
        ipRangeSample.forcePost(IpRangeSample.data)

        subIp = ipRangeSample.getInRangeIp()

        sample = self.sample
        sample.setPartyId(self.partyId)
        pk = sample.forcePost(sample.data)

        url = self.getUrl(sample.url, 'ipAddress', subIp)
        # need to pass userIdentifier as arg even when not needed
        url = '%s&partnerId=%s&userIdentifier=' % (url, self.partnerId)
        self.runGetTestByIdentifier(url, pk)

    def runGetTestByIdentifier(self, url, pk):
        sample = self.sample

        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(checkMatch(sample.data, json.loads(res.content), sample.pkName, pk), True)

    # can only update by party id
    def test_for_update(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = self.getUrl(sample.url, 'partyId', self.partyId)

        # the default content type for put is 'application/octet-stream'
        res = self.client.put(url, json.dumps(sample.updateData), content_type='application/json')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(checkMatch(sample.updateData, json.loads(res.content), sample.pkName, pk), True)
        self.assertEqual(checkMatchDB(sample.updateData, sample.model, sample.pkName, pk), True)

    # can only delete by party id
    def test_for_delete(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = self.getUrl(sample.url, 'partyId', self.partyId)

        res = self.client.delete(url)

        self.assertIsNone(TestGenericInterfaces.forceGet(sample.model,sample.pkName,pk))
        self.assertIsNone(TestGenericInterfaces.forceGet(sample.model,'partyId',self.partyId))

# test for API end point /subscriptions/activationCodes/ for create and update
# need to authenticate user
class ActivationCodeCreateAndUpdateTest(LoginRequiredTest, TestCase):
    sample = ActivationCodeSample(serverUrl)

    def setUp(self):
        super(ActivationCodeCreateAndUpdateTest, self).setUp()

        self.sample.initTransctionType()

        partnerSample = PartnerSample(serverUrl)
        partnerId = partnerSample.forcePost(partnerSample.data)
        self.sample.data['partnerId'] = self.sample.updateData['partnerId']=partnerId

    # Potential API end point threat: no role based authorization
    def test_for_create(self):
        sample = self.sample
        url = self.getUrl(sample.url)
        url = '%s&quantity=%s&period=%s&partnerId=%s&transactionType=%s' % (url, 
            1, sample.getPeriod(), sample.getPartnerId(),sample.getTransactionType())
        res = self.client.post(url)

        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(TestGenericInterfaces.forceGet(sample.model,'activationCode',json.loads(res.content)[0]))

    # update activation code as deleted
    def test_for_update(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = self.getUrl(sample.url, sample.pkName, pk)
        url += '&deleteMarker=true'
        res = self.client.put(url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(TestGenericInterfaces.forceGet(sample.model,sample.pkName,pk).deleteMarker, True)

# test for API end point /subscriptions/activationCodes/ for get and delete
# returned activation code data does not include transaction type
class ActivationCodeGetAndDeleteTest(GenericCRUDTest, TestCase):
    sample = ActivationCodeSample(serverUrl)

    def setUp(self):
        super(ActivationCodeGetAndDeleteTest, self).setUp()

        partnerSample = PartnerSample(serverUrl)
        partnerId = partnerSample.forcePost(partnerSample.data)
        self.sample.data['partnerId'] = self.sample.updateData['partnerId']=partnerId


    def test_for_get(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = self.getUrl(sample.url, sample.pkName, pk) 

        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        # transaction is not returned in API
        data = copy.deepcopy(sample.data)
        del data['transactionType']
        self.assertEqual(checkMatch(data, json.loads(res.content), sample.pkName, pk), True)

    def test_for_get_all(self):
        sample = self.sample
        pk = sample.forcePost(sample.data)
        url = self.getUrl(sample.url)

        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        # transaction is not returned in API
        data = copy.deepcopy(sample.data)
        del data['transactionType']
        self.assertEqual(checkMatch(data, json.loads(res.content), sample.pkName, pk), True)

    # Tested in above class
    def test_for_create(self):
        pass

    # Tested in above class
    def test_for_update(self):
        pass

    # delete method can be tested but shall not be used. 
    # should use update method to update delete marker instead

# test for API end point /subscriptions/transactions/
class SubscriptionTransactionCRUDTest(GenericCRUDTest, TestCase):
    sample = SubscriptionTransactionSample(serverUrl)

    def setUp(self):
        super(SubscriptionTransactionCRUDTest,self).setUp()

        partnerSample = PartnerSample(serverUrl)
        partnerId = partnerSample.forcePost(partnerSample.data)

        partySample = UserPartySample(serverUrl)
        partyId = partySample.forcePost(partySample.data)

        subscriptionSample = SubscriptionSample(serverUrl)
        subscriptionSample.setPartnerId(partnerId)
        subscriptionSample.setPartyId(partyId)
        subscriptionId = subscriptionSample.forcePost(subscriptionSample.data)

        self.sample.data['subscriptionId']=self.sample.updateData['subscriptionId']=subscriptionId

# ----------------- END OF BASIC CRUD OPERATIONS ----------------------

# Note that for subscription end points, unless specifically designed (/subscriptions/consortiums/ 
# and /subscriptions/consactsubscriptions/), otherwise they only return the subscription record of 
# the organization itself; they do not check/return the subscription of its consortium

# No API end point or method update consortiumId, consortiumStartDate and consortiumEndDate;
# they are updated by scripts/updateConsortiumSubscriptionFields.py on a daily basis by cron job 
# on API server.

# The consortiumStartDate and consortiumEndDate values are for reference only and are not used in validating 
# a subscription. Instead, when an institution or an individual that belongs to a consortium is checked for 
# authorization, the authorization end points calls method that checks not only their own subscription but 
# also the subscription of their consortium. But still, startDate and endDate of the record are used

# test for API end point /subscriptions/{subscriptionId}/renewal/
# update subscription duration directly
# will create subscription transaction
class SubscriptionRenewalTest(GenericTest, TestCase):
    sample = SubscriptionSample(serverUrl)

    def setUp(self):
        super(SubscriptionRenewalTest,self).setUp()

        partnerSample = PartnerSample(serverUrl)
        partnerId = partnerSample.forcePost(partnerSample.data)

        partySample = UserPartySample(serverUrl)
        partyId = partySample.forcePost(partySample.data)

        sample = self.sample
        sample.data['partnerId']=sample.updateData['partnerId']=partnerId
        sample.data['partyId']=sample.updateData['partyId']=partyId

    def test_for_update(self):
        sample = self.sample
        subscriptionId = sample.forcePost(sample.data)

        url = serverUrl + 'subscriptions/' + str(subscriptionId) + '/renewal/'
        # the default content type for put is 'application/octet-stream'
        res = self.client.put(url, json.dumps(sample.updateData), content_type='application/json')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(checkMatch(sample.updateData, json.loads(res.content), sample.pkName, subscriptionId), True)
        self.assertEqual(checkMatchDB(sample.updateData, sample.model, sample.pkName, subscriptionId), True)
        transactionId = json.loads(res.content)['subscriptionTransactionId']
        self.assertIsNotNone(TestGenericInterfaces.forceGet(SubscriptionTransaction,'subscriptionTransactionId',transactionId))

# test for API end point /subscriptions/payments/
# cannot test via POST request to API since not sure how to generate a stripeToken
class PostPaymentHandlingTest(ManualTest, TestCase):
    path = "/subscriptions/payments/"
    testMethodStr = "by submitting an order on ui.arabidopsis.org"

# test for API end point /subscriptions/enddate/
# end point looks for the effective subscription with latest end date that either covers the given IP address 
# or belongs to the given party for a given partner
# end point returns the expiration date of the found subscription and 'subscribed' status as True; 
# otherwise, the returned expiration date is null and status is False.
# TODO: End point cannot accept ipAddress alone without partyId or userIdentifier, which I do not see a reason to it
class GetSubcriptionEndDateTest(GenericTest, TestCase):
    partnerId = None
    userPartyId = None
    userIdentifier = None
    orgPartyId = None
    orgInRangeIp = None
    USER_SUBSCRIPTION_TYPE = 'individual'
    ORG_SUBSCRIPTION_TYPE = 'institutional'

    def setUp(self):
        super(GetSubcriptionEndDateTest,self).setUp()

        partnerSample = PartnerSample(serverUrl)
        self.partnerId = partnerSample.forcePost(partnerSample.data)

        # create individual user
        userPartySample = UserPartySample(serverUrl)
        self.userPartyId = userPartySample.forcePost(userPartySample.data)

        credentialSample = CredentialSample(serverUrl)
        credentialSample.setPartyId(self.userPartyId)
        credentialSample.setPartnerId(self.partnerId)
        credentialSample.forcePost(credentialSample.data)
        self.userIdentifier = credentialSample.getUserIdentifier()

        # create organization and its subscription
        countrySample = CountrySample(serverUrl)
        countryId = countrySample.forcePost(countrySample.data)

        orgPartySample = OrganizationPartySample(serverUrl)
        orgPartySample.setCountry(countryId)
        self.orgPartyId = orgPartySample.forcePost(orgPartySample.data)

        ipRangeSample = IpRangeSample(serverUrl)
        ipRangeSample.setPartyId(self.orgPartyId)
        ipRangeSample.forcePost(IpRangeSample.data)

        self.orgInRangeIp = ipRangeSample.getInRangeIp()

    def test_for_no_subscription(self):
        # test get by userPartyId and ipAddress when neither user nor organization is subscribed
        queryParam = 'partyId=%s&ipAddress=%s' % (self.userPartyId, self.orgInRangeIp)
        self.runTest(queryParam, False)

        # test get by userIdentifier and ipAddress when neither user nor organization is subscribed
        queryParam = 'userIdentifier=%s&ipAddress=%s' % (self.userIdentifier, self.orgInRangeIp)
        self.runTest(queryParam, False)

    def test_for_get_individual_subscription(self):       
        userSubscriptionSample = SubscriptionSample(serverUrl)
        userSubscriptionSample.setPartyId(self.userPartyId)
        userSubscriptionSample.setPartnerId(self.partnerId)
        userSubscriptionSample.forcePost(userSubscriptionSample.data)

        # test get by user partyId when user is subscribed
        queryParam = 'partyId=%s' % self.userPartyId
        self.runTest(queryParam, True, self.USER_SUBSCRIPTION_TYPE, userSubscriptionSample.getEndDate())

        # test get by user partyId and ipAddress when only user is subscribed
        queryParam = 'partyId=%s&ipAddress=%s' % (self.userPartyId, self.orgInRangeIp)
        self.runTest(queryParam, True, self.USER_SUBSCRIPTION_TYPE, userSubscriptionSample.getEndDate())

        # test get by userIdentifier when user is subscribed
        queryParam = 'userIdentifier=%s' % self.userIdentifier
        self.runTest(queryParam, True, self.USER_SUBSCRIPTION_TYPE, userSubscriptionSample.getEndDate())

        # test get by userIdentifier and ipAddress when onlyuser is subscribed
        queryParam = 'userIdentifier=%s&ipAddress=%s' % (self.userIdentifier, self.orgInRangeIp)
        self.runTest(queryParam, True, self.USER_SUBSCRIPTION_TYPE, userSubscriptionSample.getEndDate())

    def test_for_get_organization_subscription(self):
        # ip address cannot be passed alone. Need to pass individual credential (userIdentifier/partyId) 
        # as well
        orgSubscriptionSample = SubscriptionSample(serverUrl)
        orgSubscriptionSample.setPartyId(self.orgPartyId)
        orgSubscriptionSample.setPartnerId(self.partnerId)
        orgSubscriptionSample.forcePost(orgSubscriptionSample.data)

        # test get when both userIdentifier and ipAddress are provided
        queryParam = 'userIdentifier=%s&ipAddress=%s' % (self.userIdentifier, self.orgInRangeIp)
        self.runTest(queryParam, True, self.ORG_SUBSCRIPTION_TYPE, orgSubscriptionSample.getEndDate())

        # test get when both userPartyId and ipAddress are provided 
        queryParam = 'partyId=%s&ipAddress=%s' % (self.userPartyId, self.orgInRangeIp)
        self.runTest(queryParam, True, self.ORG_SUBSCRIPTION_TYPE, orgSubscriptionSample.getEndDate())

    def test_for_have_both_subscriptions(self):
        # create organization subscription before user subscription so user subscription end date is later
        orgSubscriptionSample = SubscriptionSample(serverUrl)
        orgSubscriptionSample.setPartyId(self.orgPartyId)
        orgSubscriptionSample.setPartnerId(self.partnerId)
        orgSubscriptionSample.forcePost(orgSubscriptionSample.data)

        userSubscriptionSample = SubscriptionSample(serverUrl)
        userSubscriptionSample.setPartyId(self.userPartyId)
        userSubscriptionSample.setPartnerId(self.partnerId)
        userSubscriptionSample.forcePost(userSubscriptionSample.data)

        # organization (IP based) subscription will shadow individual subscription on subscription type 
        # but end date will be the latest of both so there could be inconsistency between end date and 
        # subscription type

        expEndDate = max(orgSubscriptionSample.getEndDate(), userSubscriptionSample.getEndDate())

        # test get when both userIdentifier and ipAddress are provided
        queryParam = 'userIdentifier=%s&ipAddress=%s' % (self.userIdentifier, self.orgInRangeIp)
        self.runTest(queryParam, True, self.ORG_SUBSCRIPTION_TYPE, expEndDate)
        self.runTest(queryParam, True, self.ORG_SUBSCRIPTION_TYPE, userSubscriptionSample.getEndDate())

        # test get when both userPartyId and ipAddress are provided 
        queryParam = 'partyId=%s&ipAddress=%s' % (self.userPartyId, self.orgInRangeIp)
        self.runTest(queryParam, True, self.ORG_SUBSCRIPTION_TYPE, expEndDate)
        self.runTest(queryParam, True, self.ORG_SUBSCRIPTION_TYPE, userSubscriptionSample.getEndDate())

    def runTest(self, queryParam, expectedSubscriptionStatus, expectedSubscriptionType = None, expectedExpDate = None):
        url = '%ssubscriptions/enddate/?partnerId=%s&%s' % (serverUrl, self.partnerId, queryParam)

        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        resObj = json.loads(res.content)
        self.assertEqual(expectedSubscriptionStatus, resObj['subscribed'])
        if expectedSubscriptionType and resObj['subscriptionType']:
            self.assertEqual(expectedSubscriptionType, resObj['subscriptionType'])
        if expectedExpDate and resObj['expDate']:
            self.assertEqual(expectedExpDate, resObj['expDate'])

# test for API end point /subscriptions/membership/
# end point looks for the effective subscription with latest end date that covers the given IP address for a given partner
# end point returns the expiration date of the found subscription and 'isMember' status as True, and also
# replies the display name or organization and its logo url queried from ImageInfo table; 
# otherwise, it returns 'isMember' status as False and all other fields as None
class CheckMembershipTest(GenericTest, TestCase):
    partnerId = None
    orgPartyId = None
    orgInRangeIp = None
    imageInfoSample = ImageInfoSample()

    def setUp(self):
        super(CheckMembershipTest,self).setUp()

        partnerSample = PartnerSample(serverUrl)
        self.partnerId = partnerSample.forcePost(partnerSample.data)

        # create organization and its subscription
        countrySample = CountrySample(serverUrl)
        countryId = countrySample.forcePost(countrySample.data)

        orgPartySample = OrganizationPartySample(serverUrl)
        orgPartySample.setCountry(countryId)
        self.orgPartyId = orgPartySample.forcePost(orgPartySample.data)

        imageInfoSample = self.imageInfoSample
        imageInfoSample.setPartyId(self.orgPartyId)
        imageInfoSample.forcePost(imageInfoSample.data)

        ipRangeSample = IpRangeSample(serverUrl)
        ipRangeSample.setPartyId(self.orgPartyId)
        ipRangeSample.forcePost(IpRangeSample.data)

        self.orgInRangeIp = ipRangeSample.getInRangeIp()

    def test_for_get(self):

        # test before organization subscribes
        url = '%ssubscriptions/membership/?partnerId=%s&ipAddress=%s' % (serverUrl, self.partnerId, self.orgInRangeIp)

        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        resObj = json.loads(res.content)
        self.assertEqual(resObj['isMember'], False)

        orgSubscriptionSample = SubscriptionSample(serverUrl)
        orgSubscriptionSample.setPartyId(self.orgPartyId)
        orgSubscriptionSample.setPartnerId(self.partnerId)
        orgSubscriptionSample.forcePost(orgSubscriptionSample.data)

        # test after organization subscribes
        imageInfoSample = self.imageInfoSample
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        resObj = json.loads(res.content)
        self.assertEqual(resObj['isMember'], True)
        self.assertEqual(resObj['name'], imageInfoSample.getName())
        self.assertEqual(resObj['imageUrl'], imageInfoSample.getImageUrl())
        self.assertEqual(resObj['expDate'], orgSubscriptionSample.getEndDate())

# test for API end point /subscriptions/subscriptionrequest/
# this end point seems not working. Will print a warning to ask manual test
class SubscriptionRequestTest(ManualTest, TestCase):
    path = "/subscriptions/subscriptionrequest/"
    testMethodStr = "clicking Subcription - Download All Requests on ui.arabidopsis.org/adminportal/"

# test for API end point /subscriptions/active/
# endpoint returns ALL ACTIVE subscription and party info that covers the given IP address or belongs to the given 
# user identifier for a given partner
# ipAddress must be passed in; userIdentifier is optional
class GetActiveSubscriptionTest(GenericTest, TestCase):
    partnerId = None
    userPartySample = UserPartySample(serverUrl)
    userPartyId = None
    userIdentifier = None
    orgPartySample = OrganizationPartySample(serverUrl)
    orgPartyId = None
    orgInRangeIp = None

    def setUp(self):
        super(GetActiveSubscriptionTest,self).setUp()

        partnerSample = PartnerSample(serverUrl)
        self.partnerId = partnerSample.forcePost(partnerSample.data)

        # create individual user
        self.userPartyId = self.userPartySample.forcePost(self.userPartySample.data)

        credentialSample = CredentialSample(serverUrl)
        credentialSample.setPartyId(self.userPartyId)
        credentialSample.setPartnerId(self.partnerId)
        credentialSample.forcePost(credentialSample.data)
        self.userIdentifier = credentialSample.getUserIdentifier()

        # create organization and its subscription
        countrySample = CountrySample(serverUrl)
        countryId = countrySample.forcePost(countrySample.data)

        self.orgPartySample.setCountry(countryId)
        self.orgPartyId = self.orgPartySample.forcePost(self.orgPartySample.data)

        ipRangeSample = IpRangeSample(serverUrl)
        ipRangeSample.setPartyId(self.orgPartyId)
        ipRangeSample.forcePost(IpRangeSample.data)

        self.orgInRangeIp = ipRangeSample.getInRangeIp()

    def test_for_no_subscription(self):
        self.runTest(partyId = None, expectedPartyData = None, subscriptionId = None, expectSubscriptionData = None)

    def test_for_get_individual_subscription(self):       
        userSubscriptionSample = SubscriptionSample(serverUrl)
        userSubscriptionSample.setPartyId(self.userPartyId)
        userSubscriptionSample.setPartnerId(self.partnerId)
        subscriptionId = userSubscriptionSample.forcePost(userSubscriptionSample.data)

        self.runTest(self.userPartyId, self.userPartySample.data, subscriptionId, userSubscriptionSample.data)

    def test_for_get_organization_subscription(self):
        # ip address cannot be passed alone. Need to pass individual credential (userIdentifier/partyId) 
        # as well
        orgSubscriptionSample = SubscriptionSample(serverUrl)
        orgSubscriptionSample.setPartyId(self.orgPartyId)
        orgSubscriptionSample.setPartnerId(self.partnerId)
        subscriptionId = orgSubscriptionSample.forcePost(orgSubscriptionSample.data)

        self.runTest(self.orgPartyId, self.getOrgDataToCompare(), subscriptionId, orgSubscriptionSample.data)

    def test_for_have_both_subscriptions(self):
        orgSubscriptionSample = SubscriptionSample(serverUrl)
        orgSubscriptionSample.setPartyId(self.orgPartyId)
        orgSubscriptionSample.setPartnerId(self.partnerId)
        orgSubId = orgSubscriptionSample.forcePost(orgSubscriptionSample.data)

        userSubscriptionSample = SubscriptionSample(serverUrl)
        userSubscriptionSample.setPartyId(self.userPartyId)
        userSubscriptionSample.setPartnerId(self.partnerId)
        userSubId = userSubscriptionSample.forcePost(userSubscriptionSample.data)

        self.runTest(self.userPartyId, self.userPartySample.data, userSubId, userSubscriptionSample.data)
        self.runTest(self.orgPartyId, self.getOrgDataToCompare(), orgSubId, orgSubscriptionSample.data)

    def runTest(self, partyId = None, expectedPartyData = None, subscriptionId = None, expectSubscriptionData = None):
        # ipAddress must be passed in; userIdentifier is optional
        url = '%ssubscriptions/active/?partnerId=%s&userIdentifier=%s&ipAddress=%s' % (serverUrl, 
            self.partnerId, self.userIdentifier, self.orgInRangeIp)

        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        resObj = json.loads(res.content)
        if not partyId and not subscriptionId:
            self.assertFalse(resObj)
            return
        if partyId:
            self.assertEqual(checkMatch(expectedPartyData, resObj, 'partyId', partyId), True)
        if subscriptionId:
            self.assertEqual(checkMatch(expectSubscriptionData, resObj, 'subscriptionId', subscriptionId), True)

    def getOrgDataToCompare(self):
        # remove fields that are not returned by API end point
        return {
            'name': self.orgPartySample.getName(),
            'partyType': self.orgPartySample.getPartyType()
        }

# test for API end point /subscriptions/activesubscriptions/{partyId}/
# endpoint returns ALL ACTIVE subscriptions that belongs to a partyId for ALL partners
# end point returns {'partnerId_1':[{subscription detail}], 'partnerId_2':[{subscription detail}]...}
class GetActiveSubscriptionByPartyIdTest(GenericTest, TestCase):
    partnerId = None
    subscriptionSample = SubscriptionSample(serverUrl)

    def setUp(self):
        super(GetActiveSubscriptionByPartyIdTest,self).setUp()

        partnerSample = PartnerSample(serverUrl)
        self.partnerId = partnerSample.forcePost(partnerSample.data)

        self.subscriptionSample.setPartnerId(self.partnerId)

    def test_for_get_individual_subscription(self):
        userPartySample = UserPartySample(serverUrl)
        partyId = userPartySample.forcePost(userPartySample.data)

        self.runTest(partyId)

    def test_for_get_organization_subscription(self):
        countrySample = CountrySample(serverUrl)
        countryId = countrySample.forcePost(countrySample.data)

        orgPartySample = OrganizationPartySample(serverUrl)
        orgPartySample.setCountry(countryId)
        partyId = orgPartySample.forcePost(orgPartySample.data)

        self.runTest(partyId)

    def runTest(self, partyId):
        subscriptionSample = self.subscriptionSample
        subscriptionSample.setPartyId(partyId)
        subscriptionId = subscriptionSample.forcePost(subscriptionSample.data)

        url = '%ssubscriptions/activesubscriptions/%s/' % (serverUrl, partyId)
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(checkMatch(self.subscriptionSample.data, json.loads(res.content)[self.partnerId], 
            'subscriptionId', subscriptionId), True)

# test for API end point /subscriptions/allsubscriptions/{partyId}/
# endpoint returns ALL subscriptions that belongs to a partyId for ALL partners, including active ones
# and expired ones. Note that for each partner a party can only have an active subscription or an expired
# subscription
# end point returns {'partnerId_1':[{subscription detail}], 'partnerId_2':[{subscription detail}]...}
class GetSubscriptionHistoryByPartyIdTest(GenericTest, TestCase):
    partnerIdWithActiveSubscription = None
    partnerIdWithExpiredSubscription = None
    subscriptionSample = SubscriptionSample(serverUrl)
    expiredSubscriptionSample = SubscriptionSample(serverUrl)
    expiredSubscriptionSample.setAsExpired()

    def setUp(self):
        super(GetSubscriptionHistoryByPartyIdTest,self).setUp()

        partnerSample = PartnerSample(serverUrl)
        self.partnerIdWithActiveSubscription = partnerSample.forcePost(partnerSample.data)
        partnerSample.setDifferentPartnerId()
        self.partnerIdWithExpiredSubscription = partnerSample.forcePost(partnerSample.data)

        self.subscriptionSample.setPartnerId(self.partnerIdWithActiveSubscription)
        self.expiredSubscriptionSample.setPartnerId(self.partnerIdWithExpiredSubscription)

    def test_for_get_individual_subscription(self):
        userPartySample = UserPartySample(serverUrl)
        partyId = userPartySample.forcePost(userPartySample.data)

        self.runTest(partyId)

    def test_for_get_organization_subscription(self):
        countrySample = CountrySample(serverUrl)
        countryId = countrySample.forcePost(countrySample.data)

        orgPartySample = OrganizationPartySample(serverUrl)
        orgPartySample.setCountry(countryId)
        partyId = orgPartySample.forcePost(orgPartySample.data)

        self.runTest(partyId)

    def runTest(self, partyId):
        subscriptionSample = self.subscriptionSample
        subscriptionSample.setPartyId(partyId)
        subscriptionId = subscriptionSample.forcePost(subscriptionSample.data)

        expiredSubscriptionSample = self.expiredSubscriptionSample
        expiredSubscriptionSample.setPartyId(partyId)
        expSubscriptionId = expiredSubscriptionSample.forcePost(expiredSubscriptionSample.data)

        url = '%ssubscriptions/allsubscriptions/%s/' % (serverUrl, partyId)
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        resObj = json.loads(res.content)
        self.assertEqual(checkMatch(self.subscriptionSample.data, resObj[self.partnerIdWithActiveSubscription], 
            'subscriptionId', subscriptionId), True)
        self.assertEqual(checkMatch(self.expiredSubscriptionSample.data, resObj[self.partnerIdWithExpiredSubscription], 
            'subscriptionId', expSubscriptionId), True)

# test for API end point /subscriptions/consortiums/
# check for an institution, for each partner which of its consortium have an active subscription
# passed in partyId is the partyId of the institution
# end point returns {'partnerId_1':[{subscribed consortium data}], 'partnerId_2':[{subscribed consortium data}]...}
# DOES NOT return subscription details
# TODO: to use current API end point we have to pass in param "active" and its value has to be true, which makes
# behavior of this end point to be identical to the end point below: /subscriptions/consactsubscriptions/{partyId}
class GetConsortiumSubcriptionTest(GenericTest, TestCase):
    consortiumPartySample = ConsortiumPartySample(serverUrl)
    partnerId = None
    consortiumPartyId = None
    institutionPartyId = None

    def setUp(self):
        super(GetConsortiumSubcriptionTest,self).setUp()

        partnerSample = PartnerSample(serverUrl)
        self.partnerId = partnerSample.forcePost(partnerSample.data)

        countrySample = CountrySample(serverUrl)
        countryId = countrySample.forcePost(countrySample.data)

        parentPartySample = self.consortiumPartySample
        parentPartySample.setCountry(countryId)
        self.consortiumPartyId = parentPartyId = parentPartySample.forcePost(parentPartySample.data)

        subscriptionSample = SubscriptionSample(serverUrl)
        subscriptionSample.setPartnerId(self.partnerId)
        subscriptionSample.setPartyId(parentPartyId)
        subscriptionSample.forcePost(subscriptionSample.data)

        childPartySample = InstitutionPartySample(serverUrl)
        childPartySample.setCountry(countryId)
        self.institutionPartyId = childPartyId = childPartySample.forcePost(childPartySample.data)

        affliationSample = PartyAffiliationSample(serverUrl)
        affliationSample.setParentId(parentPartyId)
        affliationSample.setChildId(childPartyId)
        affliationSample.forcePost(affliationSample.data)

    def test_for_get(self):

        url = '%ssubscriptions/consortiums/?active=true&partyId=%s' % (serverUrl, self.institutionPartyId)

        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(checkMatch(self.consortiumPartySample.data, json.loads(res.content)[self.partnerId], 'partyId', self.consortiumPartyId), True)

# test for API end point /subscriptions/consactsubscriptions/{partyId} for Consortium Active Subscription
# check for an institution, for each partner which of its consortium have an active subscription
# passed in partyId is the partyId of the institution
# end point returns {'partnerId_1':[{subscribed consortium data}], 'partnerId_2':[{subscribed consortium data}]...}
# DOES NOT return subscription details
class GetConsortiumActiveSubscriptionTest(GenericTest, TestCase):
    consortiumPartySample = ConsortiumPartySample(serverUrl)
    partnerId = None
    consortiumPartyId = None
    institutionPartyId = None

    def setUp(self):
        super(GetConsortiumActiveSubscriptionTest,self).setUp()

        partnerSample = PartnerSample(serverUrl)
        self.partnerId = partnerSample.forcePost(partnerSample.data)

        countrySample = CountrySample(serverUrl)
        countryId = countrySample.forcePost(countrySample.data)

        parentPartySample = self.consortiumPartySample
        parentPartySample.setCountry(countryId)
        self.consortiumPartyId = parentPartyId = parentPartySample.forcePost(parentPartySample.data)

        childPartySample = InstitutionPartySample(serverUrl)
        childPartySample.setCountry(countryId)
        self.institutionPartyId = childPartyId = childPartySample.forcePost(childPartySample.data)

        affliationSample = PartyAffiliationSample(serverUrl)
        affliationSample.setParentId(parentPartyId)
        affliationSample.setChildId(childPartyId)
        affliationSample.forcePost(affliationSample.data)

    def test_for_get(self):
        url = '%ssubscriptions/consactsubscriptions/%s/' % (serverUrl, self.institutionPartyId)

        # before consortium has subscription
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(json.loads(res.content))

        subscriptionSample = SubscriptionSample(serverUrl)
        subscriptionSample.setPartnerId(self.partnerId)
        subscriptionSample.setPartyId(self.consortiumPartyId)
        subscriptionSample.forcePost(subscriptionSample.data)

        # after consortium has subcription
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(checkMatch(self.consortiumPartySample.data, json.loads(res.content)[self.partnerId], 'partyId', self.consortiumPartyId), True)

# test for API end point /subscriptions/commercials/
# Sep/03/2019: this is a dreprecated API, now replaced by SalesForce Campaign

# test for API end point /subscriptions/institutions/
# Sep/03/2019: this is a dreprecated API, now replaced by SalesForce Campaign

# test for API end point /subscriptions/request/
# Sep/03/2019: this is a dreprecated API, now replaced by SalesForce Campaign

# test for /subscriptions/templates/block or /subscriptions/templates/warn/ 
# no test as no known external resource is using them

# test for API end point /subscriptions/renew/
# an end point for sending renewal request email, assume it's deprecated

print("Running unit tests on subscription web services API.........")

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
