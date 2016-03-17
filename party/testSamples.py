import django
import unittest
import sys, getopt
from unittest import TestCase
from party.models import Party, IpRange, PartyAffiliation
from partner.models import Partner

import copy
from common.pyTests import PyTestGenerics

genericForcePost = PyTestGenerics.forcePost

class PartySample():
    path = 'parties/'
    url = None
    data = {
        'partyType':'user',
        'name':'test',
    }
    updateData = {
        'partyType':'organization',
        'name':'test1',
    }
    pkName = 'partyId'
    model = Party

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        return genericForcePost(self.model, self.pkName, data)

# TODO add sample for IPv6 tests
class IpRangeSample():
    path = 'parties/ipranges/'
    url = None
    data = {
        'start':'120.0.0.0',
        'end':'120.255.255.255',
        'partyId':1,
	'label': 'testlabel',
    }
    updateData = {
        'start':'120.0.0.0',
        'end':'120.255.211.200',
        'partyId':1,
	'label': 'labeltest',
    }
    pkName = 'ipRangeId'
    model = IpRange

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partyId'] = Party.objects.get(partyId=data['partyId'])
        return genericForcePost(self.model, self.pkName, postData)

class PartyAffiliationSample():
    path = 'parties/affiliations/'
    url = None
    data = {
        'parentPartyId': Party.objects.get(partyId=2),
        'childPartyId' : Party.objects.get(partyId=33390),
    }
    pkName = 'partyAffiliationId';
    model = PartyAffiliation
    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        return genericForcePost(self.model, self.pkName, data)

