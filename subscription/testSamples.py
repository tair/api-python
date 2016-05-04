import django
import unittest
import sys, getopt
from unittest import TestCase
from subscription.models import Subscription, SubscriptionTransaction, ActivationCode
from party.models import Party
from partner.models import Partner
import requests
import json

import copy
from common.pyTests import PyTestGenerics

genericForcePost = PyTestGenerics.forcePost

class ActivationCodeSample():
    path = 'subscriptions/activationCodes/'
    url = None
    data = {
        'activationCode':'testactivationcode',
        'partnerId':None,
        'partyId':None,
        'period':180,
        'purchaseDate':'2001-01-01T00:00:00Z',
    }
    updateData = {
        'activationCode':'testactivationcode2',
        'partnerId':None,
        'partyId':None,
        'period':150,
        'purchaseDate':'2005-01-01T00:00:00Z',
    }
    pkName = 'activationCodeId'
    model = ActivationCode

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partnerId'] = Partner.objects.get(partnerId=data['partnerId'])
        return genericForcePost(self.model, self.pkName, postData)

class SubscriptionSample():
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
        'transactionType':'create',
    }
    updateData = {
        'subscriptionId':1,
        'transactionDate':'2014-02-12T00:00:00Z',
        'startDate':'2012-04-12T00:00:00Z',
        'endDate':'2018-04-12T00:00:00Z',
        'transactionType':'renew',
    }
    pkName = 'subscriptionTransactionId'
    model = SubscriptionTransaction

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['subscriptionId'] = Subscription.objects.get(subscriptionId=data['subscriptionId'])
        return genericForcePost(self.model, self.pkName, postData)

