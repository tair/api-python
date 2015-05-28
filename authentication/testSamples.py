import django
import unittest
import sys, getopt
from unittest import TestCase
from authentication.models import UsernamePartyAffiliation
from party.models import Party
import requests
import json

import copy
from common.pyTests import PyTestGenerics

genericForcePost = PyTestGenerics.forcePost

class UsernamePartyAffiliationSample():
    partnerId = 'tair'
    path = 'subscriptions/'
    url = None
    data = {
        'username':'steve',
        'password':'stevepass',
        'email':'steve@getexp.com',
        'organization':'test organization',
        'partyId':None,
    }
    updateData = {
        'username':'steve2',
        'password':'stevepass2',
        'email':'steve@getexp.com',
        'organization':'test organization2',
        'partyId':None,
    }
    pkName = 'id'
    model = UsernamePartyAffiliation

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partyId'] = Party.objects.get(partyId=data['partyId'])
        return genericForcePost(self.model, self.pkName, postData)

