import django
import unittest
import sys, getopt
from unittest import TestCase
from subscription.models import Subscription, SubscriptionTransaction
from party.models import Party
from partner.models import Partner
import requests
import json

import copy
from common.controls import PyTestGenerics

genericForcePost = PyTestGenerics.forcePost

class SubscriptionSample():
    partnerId = 'tair'
    path = 'subscriptions/'
    url = None
    data = {
        'startDate':'2012-04-12T00:00:00Z',
        'endDate':'2018-04-12T00:00:00Z',
        'partnerId':'tair',
        'partyId':1,
    }
    updateData = {
        'startDate':'2012-04-12T00:00:00Z',
        'endDate':'2018-04-12T00:00:00Z',
        'partnerId':'cdiff',
        'partyId':1,
    }
    pkName = 'subscriptionId'
    model = Subscription

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partyId'] = Party.objects.get(partyId=data['partyId'])
        postData['partnerId'] = Partner.objects.get(partnerId=data['partnerId'])
        return genericForcePost(self.model, self.pkName, postData)


class SubscriptionTransactionSample():
    path = 'subscriptions/transactions/'
    url = None
    data = {
        'subscriptionId':1,
        'transactionDate':'2012-04-12T00:00:00Z',
        'startDate':'2012-04-12T00:00:00Z',
        'endDate':'2018-04-12T00:00:00Z',
        'transactionType':'Initial',
    }
    updateData = {
        'subscriptionId':1,
        'transactionDate':'2014-02-12T00:00:00Z',
        'startDate':'2012-04-12T00:00:00Z',
        'endDate':'2018-04-12T00:00:00Z',
        'transactionType':'Renew',
    }
    pkName = 'subscriptionTransactionId'
    model = SubscriptionTransaction

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['subscriptionId'] = Subscription.objects.get(subscriptionId=data['subscriptionId'])
        return genericForcePost(self.model, self.pkName, postData)

