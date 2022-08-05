import sys
import django
import unittest
from django.test import TestCase
from partner.models import Partner, PartnerPattern, SubscriptionTerm, SubscriptionDescription, SubscriptionDescriptionItem
import copy
from common.tests import TestGenericInterfaces

genericForcePost = TestGenericInterfaces.forcePost

class PartnerSample():
    url = None
    path = 'partners/'
    data = {
        'partnerId':'phoenix',
        'name':'phoenixTestPartner',
        'logoUri':'randomuri.com',
        'termOfServiceUri':'anotherrandomuri.com',
        'description':'Genome database for the reference plant Arabidopsis thaliana',
        'resetPasswordEmailBody': 'Test Partner username: %s (%s). Your temp password is %s.'
    }
    updateData = {
        'partnerId':'phoenix',
        'name':'phoenixTestPartner2',
        'logoUri':'randomuri2.com',
        'termOfServiceUri':'anotherrandomuri2.com',
        'description':'Updated description: Genome database for the reference plant Arabidopsis thaliana',
    }
    pkName = 'partnerId'
    model = Partner

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path
        self.data = copy.deepcopy(self.data)

    def setDifferentPartnerId(self):
        self.data['partnerId'] = 'test2'

    def forcePost(self,data):
        return genericForcePost(self.model, self.pkName, data)

class PartnerPatternSample():
    url = None
    path = 'partners/patterns/'
    data = {
        'partnerId':None,
        'sourceUri':'https://www.arabidopsis.org',
        'targetUri':'https://back-prod.arabidopsis.org',
    }
    updateData = {
        'partnerId':None,
        'sourceUri':'https://uat.arabidopsis.org',
        'targetUri':'https://back-uat.arabidopsis.org',
    }
    pkName = 'partnerPatternId'
    model = PartnerPattern

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partnerId'] = Partner.objects.get(partnerId=data['partnerId'])
        return genericForcePost(self.model, self.pkName, postData)

class SubscriptionTermSample():
    url = None
    path = 'partners/terms/'
    data = {
        'partnerId':None,
        'period':180,
        'price':180.00,
        'groupDiscountPercentage': 1.5,
        'description':'test'
    }
    updateData = {
        'partnerId':None,
        'period':365,
        'price':360.00,
        'groupDiscountPercentage': 2.5,
        'description':'test2'
    }
    pkName = 'subscriptionTermId'
    model = SubscriptionTerm

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def setPartnerId(self, partnerId):
        self.data['partnerId'] = partnerId

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partnerId'] = Partner.objects.get(partnerId=data['partnerId'])
        return genericForcePost(self.model, self.pkName, postData)

class SubscriptionDescriptionSample():
    url = None
    path = 'partners/descriptions/'
    data = {
        'partnerId':None,
        'header':'Commercial Description',
        'descriptionType':'Commercial',
    }
    updateData = {
        'partnerId':None,
        'header':'Institution Description',
        'descriptionType':'Institution',
    }
    pkName = 'subscriptionDescriptionId'
    model = SubscriptionDescription

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partnerId'] = Partner.objects.get(partnerId=data['partnerId'])
        return genericForcePost(self.model, self.pkName, postData)

class SubscriptionDescriptionItemSample():
    url = None
    path = 'partners/descriptionItems/'
    data = {
        'subscriptionDescriptionId': None,
        'text': 'Benefit'
    }
    updateData = {
        'subscriptionDescriptionId': None,
        'text': 'Updated Benefit'
    }
    pkName = 'subscriptionDescriptionItemId'
    model = SubscriptionDescriptionItem

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['subscriptionDescriptionId'] = SubscriptionDescription.objects.get(subscriptionDescriptionId=data['subscriptionDescriptionId'])
        return genericForcePost(self.model, self.pkName, postData)