import django
import unittest
import sys, getopt
from unittest import TestCase
from metering.models import IpAddressCount, LimitValue
from partner.models import Partner
import requests
import json

import copy
from common.pyTests import PyTestGenerics

genericForcePost = PyTestGenerics.forcePost

class IpAddressCountSample():
    path = 'meters/'
    url = None
    data = {
        'ip':'123.45.6.7',
        'count':1,
        'partnerId':None,
    }
    updateData = {
        'ip':'123.45.6.7',
        'count':5,
        'partnerId':None,
    }
    pkName = 'id'
    model = IpAddressCount

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partnerId'] = Partner.objects.get(partnerId=data['partnerId'])
        return genericForcePost(self.model, self.pkName, postData)

class LimitValueSample():
    path = 'meters/limits/'
    url = None
    data = {
        'val':8,
        'partnerId':None,
    }
    updateData = {
        'val':12,
        'partnerId':None,
    }
    pkName = 'limitId'
    model = LimitValue

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partnerId'] = Partner.objects.get(partnerId=data['partnerId'])
        return genericForcePost(self.model, self.pkName, postData)
