import django
import unittest
import sys
import copy
from unittest import TestCase
from party.models import Country, Party, IpRange, PartyAffiliation, ImageInfo
from partner.models import Partner
from common.tests import TestGenericInterfaces
from datetime import datetime, timedelta

genericForcePost = TestGenericInterfaces.forcePost

class CountrySample():
    path = 'parties/countries/'
    url = None
    data = {
        'name': 'United States'
    }
    updateData = {
        'name': 'China'
    }
    pkName = 'countryId'
    model = Country

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def getName(self):
        return self.data['name']

    def forcePost(self,data):
        return genericForcePost(self.model, self.pkName, data)

class UserPartySample():
    path = 'parties/'
    url = None
    PARTY_TYPE_USER = 'user'
    PARTY_TYPE_STAFF = 'staff'
    PARTY_TYPE_ADMIN = 'admin'
    data = {
        'partyType':PARTY_TYPE_USER,
        'name':'test_user',
    }
    updateData = {
        'partyType':PARTY_TYPE_USER,
        'name':'test_user_II',
    }
    pkName = 'partyId'
    model = Party

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        return genericForcePost(self.model, self.pkName, data)

class OrganizationPartySample():
    path = 'parties/'
    url = None
    PARTY_TYPE_ORG = 'organization'
    data = {
        'partyType':PARTY_TYPE_ORG,
        'name':'test_organization',
        'display': True,
        'country': None,
        'label': 'Test Label'
    }
    updateData = {
        'partyType':PARTY_TYPE_ORG,
        'name':'test_organization_II',
        'display': False,
        'country': None,
        'label': 'Test Label II'
    }
    pkName = 'partyId'
    model = Party

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def getName(self):
        return self.data['name']

    def getPartyType(self):
        return self.data['partyType']

    def setCountry(self, countryId):
        self.data['country'] = countryId

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['country'] = Country.objects.get(countryId=data['country'])
        return genericForcePost(self.model, self.pkName, postData)

class InstitutionPartySample(OrganizationPartySample):
    path = 'parties/institutions/'

class ConsortiumPartySample():
    path = 'parties/consortiums/'
    url = None
    PARTY_TYPE_CONSORTIUM = 'consortium'
    data = {
        'partyType':PARTY_TYPE_CONSORTIUM,
        'name':'test_consortium',
        'display': True,
        'country': None,
        'label': 'Test Label'
    }
    updateData = {
        'partyType':PARTY_TYPE_CONSORTIUM,
        'name':'test_consortium_II',
        'display': False,
        'country': None,
        'label': 'Test Label II'
    }
    pkName = 'partyId'
    model = Party

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def setCountry(self, countryId):
        self.data['country'] = countryId

    def getName(self):
        return self.data['name']

    def getPartyType(self):
        return self.data['partyType']

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['country'] = Country.objects.get(countryId=data['country'])
        return genericForcePost(self.model, self.pkName, postData)

# TODO: add sample for IPv6 tests
# TODO: test for 'ip range too large' type of IP ranges - API needs to be 
# updated. Should not throw unwrapped error
class IpRangeSample():
    path = 'parties/ipranges/'
    url = None
    data = {
        'start':'120.10.20.0',
        'end':'120.10.22.255',
        'partyId': None,
        'label': 'test_label',
    }
    updateData = {
        'start':'120.10.20.0',
        'end':'120.10.23.80',
        'partyId': None,
        'label': 'test_label_II',
    }
    pkName = 'ipRangeId'
    model = IpRange

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def setPartyId(self, partyId):
        self.data['partyId'] = partyId

    def getInRangeIp(self):
        return '120.10.21.231'

    def getOutRangeIp(self):
        return '133.1.8.52'

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partyId'] = Party.objects.get(partyId=data['partyId'])
        return genericForcePost(self.model, self.pkName, postData)

class PartyAffiliationSample():
    path = 'parties/affiliations/'
    url = None
    data = {
        'parentPartyId': None,
        'childPartyId' : None,
    }
    pkName = 'partyAffiliationId';
    model = PartyAffiliation

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def setParentId(self, parentPartyId):
        self.data['parentPartyId'] = parentPartyId

    def getParentId(self):
        return self.data['parentPartyId']

    def setChildId(self, childPartyId):
        self.data['childPartyId'] = childPartyId

    def getChildId(self):
        return self.data['childPartyId']

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['parentPartyId'] = Party.objects.get(partyId=data['parentPartyId'])
        postData['childPartyId'] = Party.objects.get(partyId=data['childPartyId'])
        return genericForcePost(self.model, self.pkName, postData)

class ImageInfoSample():
    data = {
        'partyId': None,
        'name' : 'Test Organization',
        'imageUrl': 'somerandomurl'
    }
    pkName = 'imageInfoId';
    model = ImageInfo

    def setPartyId(self, partyId):
        self.data['partyId'] = partyId

    def getName(self):
        return self.data['name']

    def getImageUrl(self):
        return self.data['imageUrl']

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partyId'] = Party.objects.get(partyId=data['partyId'])
        return genericForcePost(self.model, self.pkName, postData)

class UsageSample():
    PARTNER = 'phoenix'
    COMMENTS = 'Please send us the usage data'
    NUM_DAYS_DELTA = 90
    RECEIPIENT_EMAIL = 'xingguo.chen@arabidopsis.org'
    startDateObj = datetime.today() - timedelta(days=NUM_DAYS_DELTA)
    startDate = startDateObj.strftime('%b %d, %Y')
    endDateObj = datetime.today()
    endDate = endDateObj.strftime('%b %d, %Y')
    institutionData = {
        'institution': 'University of Mars',
        'consortium': None,
        'name': 'Science Library',
        'partner': PARTNER,
        'email': 'science@umars.edu',
        'startDate': startDate,
        'endDate': endDate,
        'comments': COMMENTS
    }
    consortiumData = {
        'institution': None,
        'consortium': 'Galaxy University Association',
        'name': 'Central Library',
        'partner': PARTNER,
        'email': 'library@gua.edu',
        'startDate': startDate,
        'endDate': endDate,
        'comments': COMMENTS
    }
