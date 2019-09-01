#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.                                                                                                                                  

import django
import unittest
import sys
import json
from django.test import TestCase
from common.tests import TestGenericInterfaces, GenericCRUDTest, GenericTest
from party.testSamples import UserPartySample, OrganizationPartySample, IpRangeSample, CountrySample
from partner.testSamples import PartnerSample
from authentication.testSamples import CredentialSample
from subscription.testSamples import SubscriptionSample
from testSamples import UriPatternSample, AccessRuleSample, AccessTypeSample
from authorization.models import Status
# Python 3: module Cookie -> http.cookies
from Cookie import SimpleCookie

# Create your tests here.                                                                                                                                                                                 
django.setup()
serverUrl = TestGenericInterfaces.getHost()

# ---------------------- UNIT TEST FOR BASIC CRUD OPERATIONS -------------

# Test for API end point /authorizations/patterns/
class UriPatternCRUDTest(GenericCRUDTest, TestCase):
    sample = UriPatternSample(serverUrl)

# Test for API end point /authorizations/accessTypes/
class AccessTypesCRUDTest(GenericCRUDTest, TestCase):
    sample = AccessTypeSample(serverUrl)

# Test for API end point /authorizations/accessRules/
class AccessRuleCRUDTest(GenericCRUDTest, TestCase):
    sample = AccessRuleSample(serverUrl)
    
    def setUp(self):
        super(AccessRuleCRUDTest,self).setUp()
        partnerSample = PartnerSample(serverUrl)
        partnerId = partnerSample.forcePost(partnerSample.data)
        self.sample.data['partnerId']=self.sample.updateData['partnerId']=partnerId

        patternSample = UriPatternSample(serverUrl)
        patternId = patternSample.forcePost(patternSample.data)
        self.sample.data['patternId']=patternId

        accessTypeSample = AccessTypeSample(serverUrl)
        accessTypeId = accessTypeSample.forcePost(accessTypeSample.data)
        self.sample.data['accessTypeId']=accessTypeId

    def test_for_update(self):
        # set different pattern for update data
        patternSample = UriPatternSample(serverUrl)
        updatePatternId = patternSample.forcePost(patternSample.updateData)
        self.sample.updateData['patternId']=updatePatternId
        
        # set different access type for update data
        accessTypeSample = AccessTypeSample(serverUrl)
        updateAccessTypeId = accessTypeSample.forcePost(accessTypeSample.updateData)
        self.sample.updateData['accessTypeId']=updateAccessTypeId

        super(AccessRuleCRUDTest, self).test_for_update()


# # ----------------- END OF BASIC CRUD OPERATIONS ----------------------

# Base class for sample management for access, subscription, and authorization access tests.
class GenericAuthorizationTest(GenericTest, TestCase):
    partnerId = None
    patternId = None
    patternSample = UriPatternSample(serverUrl)
    accessRuleSample = AccessRuleSample(serverUrl)

    def setUp(self):
        super(GenericAuthorizationTest, self).setUp()

        partnerSample = PartnerSample(serverUrl)
        self.partnerId = partnerSample.forcePost(partnerSample.data)
        self.accessRuleSample.data['partnerId'] = self.partnerId

        patternId = self.patternSample.forcePost(self.patternSample.data)
        self.accessRuleSample.data['patternId'] = patternId

    def setUpLoginAccessRule(self):
        accessTypeSample = AccessTypeSample(serverUrl)
        accessTypeSample.setAsLoginType()
        accessTypeId = accessTypeSample.forcePost(accessTypeSample.data)

        self.accessRuleSample.data['accessTypeId'] = accessTypeId
        self.accessRuleSample.forcePost(self.accessRuleSample.data)

    def setUpPaidAccessRule(self):
        accessTypeSample = AccessTypeSample(serverUrl)
        accessTypeSample.setAsPaidType()
        accessTypeId = accessTypeSample.forcePost(accessTypeSample.data)

        self.accessRuleSample.data['accessTypeId'] = accessTypeId
        self.accessRuleSample.forcePost(self.accessRuleSample.data)

    def setUpSubscribedUser(self):
        credentialSample = self.setUpCredentialSample()

        individualSubscriptionSample = SubscriptionSample(serverUrl)
        individualSubscriptionSample.data['partnerId'] = self.partnerId
        individualSubscriptionSample.data['partyId'] = credentialSample.getPartyId()
        individualSubscriptionSample.forcePost(individualSubscriptionSample.data)

        return credentialSample

    def setUpCredentialSample(self):
        userPartySample = UserPartySample(serverUrl)
        userPartyId = userPartySample.forcePost(userPartySample.data)

        credentialSample = CredentialSample(serverUrl)

        credentialSample.setPartnerId(self.partnerId)
        credentialSample.setPartyId(userPartyId)
        credentialSample.forcePost(credentialSample.data)
        
        return credentialSample

    def setUpSubscribedOrganization(self):
        countrySample = CountrySample(serverUrl)
        countryId = countrySample.forcePost(countrySample.data)

        organizationPartySample = OrganizationPartySample(serverUrl)
        organizationPartySample.data['country'] = countryId
        organizationPartyId = organizationPartySample.forcePost(organizationPartySample.data)

        orgIpRangeSample = IpRangeSample(serverUrl)
        orgIpRangeSample.data['partyId'] = organizationPartyId
        orgIpRangeSample.forcePost(orgIpRangeSample.data)

        organizationSubscriptionSample = SubscriptionSample(serverUrl)
        organizationSubscriptionSample.data['partnerId'] = self.partnerId
        organizationSubscriptionSample.data['partyId'] = organizationPartyId
        organizationSubscriptionSample.forcePost(organizationSubscriptionSample.data)

        return orgIpRangeSample

# Test for API end point /authorizations/authentications/
# Checks if user can access a Login type pattern
# End point returns true if url to check does not require login or user already logins
# Returns false when url requires login and user is not logged in
# ApiKey, credentialId and secretKey are required and need to be passed in by cookie
class AuthenticationTest(GenericAuthorizationTest):
    url = serverUrl+'authorizations/authentications/'
    loginPattern = None
    nonLoginPattern = None
    credentialSample = None

    def setUp(self):
        super(AuthenticationTest,self).setUp()
        
        self.setUpLoginAccessRule()
        self.loginPattern = self.patternSample.data['pattern']
        self.nonLoginPattern = self.patternSample.updateData['pattern']

        # create user credential and its subscription
        self.credentialSample = self.setUpCredentialSample()

    def test_for_authentication(self):
        self.client.cookies = SimpleCookie({'apiKey':self.apiKey})
        
        # test login not required pattern when user is not logged in
        self.runAuthenticationTest(self.nonLoginPattern, True)

        # test login required pattern when user is not logged in
        self.runAuthenticationTest(self.loginPattern, False)

        # test login required pattern when user is logged in
        credentialSample = self.credentialSample
        cookies = SimpleCookie({'apiKey':self.apiKey, 'credentialId':credentialSample.getPartyId(), 'secretKey':credentialSample.getSecretKey()})
        self.runAuthenticationTest(self.loginPattern, True, cookies)

    def runAuthenticationTest(self, urlToCheck, expectedStatus, cookies = None):
        url = '%s?partnerId=%s&url=%s' % (self.url, self.partnerId, urlToCheck)
        if cookies:
            self.client.cookies = cookies
        else:
            self.client.cookies = SimpleCookie({'apiKey':self.apiKey})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content)['access'], expectedStatus)  

# Test for API end point /authorizations/subscriptions/
# Checks if an user (by partyId) or an IP address can access a Paid (subsription required) 
# type pattern
# End point returns true if url to check does not require subscription or if user
# or ip address belongs to a subscribed entity
# Returns false when url requires subscription and no subscribed entity detected
class SubscriptionTest(GenericAuthorizationTest):
    url = serverUrl + 'authorizations/subscriptions/'
    paidPattern = None
    nonPaidPattern = None
    userPartyId = None
    orgIpRangeSample = IpRangeSample(serverUrl)

    def setUp(self):
        super(SubscriptionTest,self).setUp()

        self.setUpPaidAccessRule()
        self.paidPattern = self.patternSample.data['pattern']
        self.nonPaidPattern = self.patternSample.updateData['pattern']

        credentialSample = self.setUpSubscribedUser()
        self.userPartyId = credentialSample.getPartyId()

        self.orgIpRangeSample = self.setUpSubscribedOrganization()

    def test_for_subscription(self):
        # User with subscription, Paid url. access should be True
        # Note if a non-exist partyId is passed in an error will be thrown
        authParam = 'partyId=%s' % self.userPartyId
        self.runSubscriptionTest(self.paidPattern, authParam , True)
        
        # IP of organization with subscription, Paid url, access should be True
        subscribedIP = self.orgIpRangeSample.getInRangeIp()
        authParam = 'ip=%s' % subscribedIP
        self.runSubscriptionTest(self.paidPattern, authParam, True) 

        # IP outside of organization with subscription, Paid url, access should be False
        # Note that if an invalid format IP is passed in, error will be thrown
        unsubscribedIP = self.orgIpRangeSample.getOutRangeIp()
        authParam = 'ip=%s' % unsubscribedIP
        self.runSubscriptionTest(self.paidPattern, authParam, False) 
        
        # No identity info, Paid url. access should be False
        self.runSubscriptionTest(self.paidPattern, None, False)

        # Not Paid url. access should be True
        self.runSubscriptionTest(self.nonPaidPattern, None, True)

    def runSubscriptionTest(self, urlToCheck, authParam, expectedStatus):
        url = '%s?partnerId=%s&url=%s' % (self.url, self.partnerId, urlToCheck)
        if authParam:
            url = '%s&%s' % (url, authParam)

        self.client.cookies = SimpleCookie({'apiKey':self.apiKey})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(json.loads(res.content)['access'], expectedStatus)

# Test for API end point /authorizations/access/
# Checks if a url pattern requires subscription and if an IP address or a list of IP addresses 
# can access this pattern
# End point returns a JSON object, which includes but not limited to
# (1) status as either "NeedLogin" (for pattern that requires login, this checks before subscription status) 
# or "OK" (for free pattern or paid pattern + subscribed IP) or  "NeedSubscription" (paid pattern + 
# unsubscribed IP)
# (2) isPaidContent as "T" (paid pattern) or "F" (free pattern)
# (3) userIdentifier for the passed in credentialId and secretKey
# ApiKey, credentialId and secretKey are required and need to be passed in by cookie
class AccessTest(GenericAuthorizationTest):
    url = serverUrl + 'authorizations/access/'
    credentialSample = None
    orgIpRangeSample = None

    def setUp(self):
        super(AccessTest, self).setUp()

        self.credentialSample = self.setUpSubscribedUser()

        self.orgIpRangeSample = self.setUpSubscribedOrganization()

    def test_for_login_only_access(self):
        self.setUpLoginAccessRule()
        loginPattern = self.patternSample.data['pattern']
        nonLoginPattern = self.patternSample.updateData['pattern']

        credentialSample = self.credentialSample

        # test login not required & free pattern when user is not logged in, status should be OK
        self.runAccessTest(urlToCheck=nonLoginPattern, expectedUrlPaidStatus=False,
            authParam=None, ipList=None, expectedNeedLoginStatus=False, 
            expectedAccessStatus=True, expectedUserIdentifier=None, cookies=None)

        # test login required & free pattern when user is not logged in, status should be NeedLogin
        self.runAccessTest(urlToCheck=loginPattern, expectedUrlPaidStatus=False, 
            authParam=None, ipList=None, expectedNeedLoginStatus=True, 
            expectedAccessStatus=None, expectedUserIdentifier=None, cookies=None)

        # test valid credential + login required & free url, status should be OK
        partyId = credentialSample.getPartyId()
        # note this partyId can be different from the credentialId we passed in cookies, and the user identifier 
        # returned is in accordance with this partyId. For the sake of consistency we use same id in the test
        authParam = 'partyId=%s' % partyId
        cookies = SimpleCookie({'apiKey':self.apiKey, 'credentialId':partyId, 'secretKey':credentialSample.getSecretKey()})
        self.runAccessTest(urlToCheck=loginPattern, expectedUrlPaidStatus=False, 
            authParam=authParam, ipList=None, expectedNeedLoginStatus=False, 
            expectedAccessStatus=True, expectedUserIdentifier=credentialSample.getUserIdentifier(), cookies=cookies)

    def test_for_subscription_only_access(self):
        self.setUpPaidAccessRule()
        paidPattern = self.patternSample.data['pattern']
        nonPaidPattern = self.patternSample.updateData['pattern']

        credentialSample = self.credentialSample
        orgIpRangeSample = self.orgIpRangeSample

        # test no credential & ip for paid url, status should be NeedSubscription
        self.runAccessTest(urlToCheck=paidPattern, expectedUrlPaidStatus=True, 
            authParam=None, ipList=None, expectedNeedLoginStatus=False, 
            expectedAccessStatus=False, expectedUserIdentifier=None, cookies=None)

        # test no credential & ip for free url, status should be OK
        self.runAccessTest(urlToCheck=nonPaidPattern, expectedUrlPaidStatus=False, 
            authParam=None, ipList=None, expectedNeedLoginStatus=False, 
            expectedAccessStatus=True, expectedUserIdentifier=None, cookies=None)

        # test valid subscription for individual, paid url, status should be OK
        partyId = credentialSample.getPartyId()
        authParam = 'partyId=%s' % partyId
        cookies = SimpleCookie({'apiKey':self.apiKey, 'credentialId':partyId, 'secretKey':credentialSample.getSecretKey()})
        self.runAccessTest(urlToCheck=paidPattern, expectedUrlPaidStatus=True, 
            authParam=authParam, ipList=None, expectedNeedLoginStatus=False, 
            expectedAccessStatus=True, expectedUserIdentifier=credentialSample.getUserIdentifier(), cookies=cookies)
        
        # test valid subscription for organization, paid url, status should be OK
        subscribedIP = self.orgIpRangeSample.getInRangeIp()
        self.runAccessTest(urlToCheck=paidPattern, expectedUrlPaidStatus=True, 
            authParam=None, ipList=subscribedIP, expectedNeedLoginStatus=False, 
            expectedAccessStatus=True, expectedUserIdentifier=None, cookies=None)

        # test IP outside of subscribed organization subscription, paid url, status should be NeedSubscription
        unsubscribedIP = self.orgIpRangeSample.getOutRangeIp()
        self.runAccessTest(urlToCheck=paidPattern, expectedUrlPaidStatus=True, 
            authParam=None, ipList=unsubscribedIP, expectedNeedLoginStatus=False, 
            expectedAccessStatus=False, expectedUserIdentifier=None, cookies=None)

    def test_for_login_and_subscription_access(self):
        self.setUpLoginAccessRule()
        self.setUpPaidAccessRule()
        loginPaidPattern = self.patternSample.data['pattern']

        # test login required & paid pattern when no user nor IP provided, status should be NeedLogin
        self.runAccessTest(urlToCheck=loginPaidPattern, expectedUrlPaidStatus=True,
            authParam=None, ipList=None, expectedNeedLoginStatus=True, 
            expectedAccessStatus=None, expectedUserIdentifier=None, cookies=None)

        # test login required & paid pattern when only IP provided, status should be NeedLogin
        subscribedIP = self.orgIpRangeSample.getInRangeIp()
        self.runAccessTest(urlToCheck=loginPaidPattern, expectedUrlPaidStatus=True, 
            authParam=None, ipList=subscribedIP, expectedNeedLoginStatus=True, 
            expectedAccessStatus=None, expectedUserIdentifier=None, cookies=None)

        # test login required & paid pattern with subscribed user , status should be OK
        credentialSample = self.credentialSample
        partyId = credentialSample.getPartyId()
        authParam = 'partyId=%s' % partyId
        cookies = SimpleCookie({'apiKey':self.apiKey, 'credentialId':partyId, 'secretKey':credentialSample.getSecretKey()})
        self.runAccessTest(urlToCheck=loginPaidPattern, expectedUrlPaidStatus=True, 
            authParam=authParam, ipList=None, expectedNeedLoginStatus=False, 
            expectedAccessStatus=True, expectedUserIdentifier=credentialSample.getUserIdentifier(), cookies=cookies)
        
        # create additional credential that is not subscribed
        nonSubUserPartySample = UserPartySample(serverUrl)
        nonSubUserPartyId = nonSubUserPartySample.forcePost(nonSubUserPartySample.updateData)

        nonSubcredentialSample = CredentialSample(serverUrl)
        nonSubcredentialSample.setAsUpdateExample()
        nonSubcredentialSample.setPartnerId(self.partnerId)
        nonSubcredentialSample.setPartyId(nonSubUserPartyId)
        nonSubcredentialSample.forcePost(nonSubcredentialSample.data)
        
        # test login required & paid pattern with unsubscribed user , status should be NeedSubscription
        partyId = nonSubcredentialSample.getPartyId()
        authParam = 'partyId=%s' % partyId
        cookies = SimpleCookie({'apiKey':self.apiKey, 'credentialId':partyId, 'secretKey':nonSubcredentialSample.getSecretKey()})
        self.runAccessTest(urlToCheck=loginPaidPattern, expectedUrlPaidStatus=True, 
            authParam=authParam, ipList=None, expectedNeedLoginStatus=False, 
            expectedAccessStatus=False, expectedUserIdentifier=nonSubcredentialSample.getUserIdentifier(), cookies=cookies)

    # Note ipList param always need to add to end point call even when no value for it
    def runAccessTest(self, urlToCheck, expectedUrlPaidStatus, authParam = None, ipList = None,
        expectedNeedLoginStatus = None, expectedAccessStatus = None,  expectedUserIdentifier = None, cookies = None):
        if not ipList:
            ipList = ''
        url = '%s?partnerId=%s&url=%s&ipList=%s' % (self.url, self.partnerId, urlToCheck, ipList)
        if authParam:
            url = '%s&%s' % (url, authParam)

        if cookies:
            self.client.cookies = cookies
        else:
            self.client.cookies = SimpleCookie({'apiKey':self.apiKey})
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        res = json.loads(res.content)
        status = ''
        if expectedNeedLoginStatus is not None and expectedNeedLoginStatus:
            status = Status.needLogin
        if expectedAccessStatus is not None:
            if expectedAccessStatus:
                status = Status.ok
            else:
                status = Status.needSubscription
        self.assertEqual(res['status'], status)
        if expectedUrlPaidStatus:
            isPaidContent = 'T'
        else:
            isPaidContent = 'F'
        self.assertEqual(res['isPaidContent'], isPaidContent)
        if expectedUserIdentifier:
            self.assertEqual(res['userIdentifier'], str(expectedUserIdentifier))

print "Running unit tests on authorization web services API........."

if __name__ == '__main__':
    sys.argv[1:] = []
    unittest.main()
    ret = not runner.run(suite).wasSuccessful()
    sys.exit(ret)
