import sys
import django
import unittest
from unittest import TestCase
from partner.models import Partner, PartnerPattern, SubscriptionTerm, SubscriptionDescription, SubscriptionDescriptionItem
import copy
from common.pyTests import PyTestGenerics

genericForcePost = PyTestGenerics.forcePost

class PartnerSample():
    url = None
    path = 'partners/'
    data = {
        'partnerId':'test',
        'name':'testPartner',
        'logoUri':'randomuri.com',
        'termOfServiceUri':'anotherrandomuri.com',
        'description':'Genome database for the reference plant Arabidopsis thaliana',
    }
    updateData = {
        'partnerId':'test',
        'name':'testPartner2',
        'logoUri':'randomuri.com',
        'termOfServiceUri':'anotherrandomuri.com',
        'description':'Genome database for the reference plant Arabidopsis thaliana2',
    }
    pkName = 'partnerId'
    model = Partner

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

        #delete possible entries that we use as test case
        try:
            filters={self.pkName:self.data['patternId']}
            self.model.objects.get(**filters).delete()
        except:
            pass

    def forcePost(self,data):
        return genericForcePost(self.model, self.pkName, data)

class PartnerPatternSample():
    url = None
    path = 'partners/patterns/'
    data = {
        'partnerId':None,
        'sourceUri':'https://paywall2.steveatgetexp.com',
        'targetUri':'https://back-prod.steveatgetexp.com',
    }
    updateData = {
        'partnerId':None,
        'sourceUri':'https://paywall2a.steveatgetexp.com',
        'targetUri':'https://back-prod.steveatgetexp.com',
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
        'price':360.00,
        'groupDiscountPercentage':0.7,
        'description':'test'
    }
    updateData = {
        'partnerId':None,
        'period':365,
        'price':180.00,
        'groupDiscountPercentage':0.8,
        'description':'test2'
    }
    pkName = 'subscriptionTermId'
    model = SubscriptionTerm

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partnerId'] = Partner.objects.get(partnerId=data['partnerId'])
        return genericForcePost(self.model, self.pkName, postData)

class SubscriptionDescriptionSample():
    url = None
    path = 'partners/descriptions/'
    data = {
        'header':'Commercial Description',
        'descriptionType':'Commercial',
        'partnerId':None,
    }
    updateData = {
        'header':'Commercial Description2',
        'descriptionType':'Institution',
        'partnerId':None,
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
        'subscriptionDescriptionId':None,
    }
    updateData = {
        'subscriptionDescriptionId':None,
    }
    pkName = 'subscriptionDescriptionItemId'
    model = SubscriptionDescriptionItem

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['subscriptionDescritpionId'] = SubscriptionDescription.objects.get(subscriptionDescriptionId=data['subscriptionDescriptionId'])
        return genericForcePost(self.model, self.pkName, postData)
