#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

import django
import unittest
import sys, getopt
import requests
from unittest import TestCase
from authorization.models import UriPattern, AccessRule, AccessType
from authentication.models import User
from partner.models import Partner
from party.models import Party
from common.pyTests import PyTestGenerics

from authorization.models import Status
import copy

genericForcePost = PyTestGenerics.forcePost


class UriPatternSample():
    url = None
    path = 'authorizations/patterns/'
    data = {
        'pattern':'/news/'
    }
    updateData = {
        'pattern':'/news2/'
    }
    pkName = 'patternId'
    model = UriPattern

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        return genericForcePost(self.model, self.pkName, data)

class AccessRuleSample():
    partnerId = 'tair'
    url = None
    path = 'authorizations/accessRules/'
    data = {
        'accessRuleId':1,
        'patternId':1,
        'accessTypeId':1,
        'partnerId':'tair',
    }

    updateData = {
        'accessRuleId':1,
        'patternId':7,
        'accessTypeId':1,
        'partnerId':'cdiff',
    }
    pkName = 'accessRuleId'
    model = AccessRule

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['patternId'] = UriPattern.objects.get(patternId=data['patternId'])
        postData['accessTypeId'] = AccessType.objects.get(accessTypeId=data['accessTypeId'])
        postData['partnerId'] = Partner.objects.get(partnerId=data['partnerId'])
        return genericForcePost(self.model, self.pkName, postData)

class AccessTypeSample():
    url = None
    path = 'authorizations/accessTypes/'
    data = {
        'name':'test1',
    }

    updateData = {
        'name':'test2',
    }
    pkName = 'accessTypeId'
    model = AccessType

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        return genericForcePost(self.model, self.pkName, data)


class UserSample():
    data = {
        'username':'steve',
        'password':'stevepass',
        'email':'steve@getexp.com',
        'institution':'test organization',
        'partyId':None,
        'partnerId':None,
        'userIdentifier':'1234536',
    }
    pkName = 'id'
    model = User

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partyId'] = Party.objects.get(partyId=data['partyId'])
        postData['partnerId'] = Partner.objects.get(partnerId=data['partnerId'])
        return genericForcePost(self.model, self.pkName, postData)

