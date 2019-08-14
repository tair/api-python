#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from authorization.models import UriPattern, AccessRule, AccessType
from partner.models import Partner
from party.models import Party
from common.tests import TestGenericInterfaces
import copy
import hashlib

genericForcePost = TestGenericInterfaces.forcePost

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

    def forcePost(self,postData):
        return genericForcePost(self.model, self.pkName, postData)

class AccessRuleSample():
    partnerId = 'tair'
    url = None
    path = 'authorizations/accessRules/'
    data = {
        'partnerId':None,
        'patternId':None,
        'accessTypeId':None,
    }

    updateData = {
        'partnerId':None,
        'patternId':None,
        'accessTypeId':None,
    }
    pkName = 'accessRuleId'
    model = AccessRule

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,postData):
        processedData = copy.deepcopy(postData)
        processedData['patternId'] = UriPattern.objects.get(patternId=postData['patternId'])
        processedData['accessTypeId'] = AccessType.objects.get(accessTypeId=postData['accessTypeId'])
        processedData['partnerId'] = Partner.objects.get(partnerId=postData['partnerId'])
        return genericForcePost(self.model, self.pkName, processedData)

class AccessTypeSample():
    url = None
    path = 'authorizations/accessTypes/'
    TYPE_LOGIN = 'Login'
    TYPE_PAID = 'Paid'
    data = {
        'name':TYPE_LOGIN,
    }
    updateData = {
        'name':TYPE_PAID,
    }
    pkName = 'accessTypeId'
    model = AccessType

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def setAsLoginType(self):
        self.data['name'] = self.TYPE_LOGIN

    def setAsPaidType(self):
        self.data['name'] = self.TYPE_PAID

    def forcePost(self,postData):
        return genericForcePost(self.model, self.pkName, postData)