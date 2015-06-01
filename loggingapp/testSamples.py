import django
import unittest
import sys, getopt
from unittest import TestCase
from subscription.models import Subscription, SubscriptionTransaction
from loggingapp.models import PageView
from party.models import Party
from partner.models import Partner
import requests
import json

import copy
from common.pyTests import PyTestGenerics

genericForcePost = PyTestGenerics.forcePost

class PageViewSample():
    path = 'session-logs/page-views/'
    url = None
    data = {
        'uri':'test123',
        'partyId':None,
        'pageViewDate':'2013-08-31T00:00:00Z',
        'sessionId':'abcdefg'
    }
    updateData = {
        'uri':'test234',
        'partyId':None,
        'pageViewDate':'2020-08-31T00:00:00Z',
        'sessionId':'efghijk'
    }
    pkName = 'pageViewId'
    model = PageView

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partyId'] = Party.objects.get(partyId=data['partyId'])
        return genericForcePost(self.model, self.pkName, postData)


