import sys
import django
import unittest
from unittest import TestCase
from partner.models import Partner, PartnerPattern, SubscriptionTerm
import copy
from common.controls import PyTestGenerics

genericForcePost = PyTestGenerics.forcePost

class PartnerSample():
    url = None
    path = 'partners/'
    data = {
        'partnerId':'test',
        'name':'testPartner',
    }
    updateData = {
        'partnerId':'test',
        'name':'testPartner2',
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
    partnerId = 'cdiff'
    data = {
        'partnerId':'cdiff',
        'pattern':'/test/',
    }
    updateData = {
        'partnerId':'tair',
        'pattern':'/test2/',
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
    partnerId='tair'
    url = None
    path = 'partners/terms/'
    data = {
        'partnerId':'tair',
        'period':180,
        'price':360.00,
        'groupDiscountPercentage':0.7,
    }
    updateData = {
        'partnerId':'tair',
        'period':365,
        'price':180.00,
        'groupDiscountPercentage':0.8,
    }
    pkName = 'subscriptionTermId'
    model = SubscriptionTerm

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partnerId'] = Partner.objects.get(partnerId=data['partnerId'])
        return genericForcePost(self.model, self.pkName, postData)
