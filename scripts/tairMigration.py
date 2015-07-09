#!/usr/bin/python                                                                                                                                                                                                                                                             
import django
import os

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()
from partner.models import Partner, PartnerPattern, SubscriptionTerm, SubscriptionDescription, SubscriptionDescriptionItem
from partner.serializers import PartnerSerializer, PartnerPatternSerializer, SubscriptionTermSerializer, SubscriptionDescriptionSerializer, SubscriptionDescriptionItemSerializer
from apikey.serializers import ApiKeySerializer
from authorization.serializers import AccessTypeSerializer, AccessRuleSerializer, UriPatternSerializer
from metering.serializers import LimitValueSerializer

import tairSetting

APIKEY = [
    {'apiKey':'test123'},
]

TAIR = {
    'Partner':{
        'partnerId':'tair',
        'name':'TAIR',
        'logoUri':'https://s3-us-west-2.amazonaws.com/pw2-logo/logo2.gif',
        'termOfServiceUri':'https://www.arabidopsis.org/doc/about/tair_terms_of_use/417',
    },
    'PartnerPattern':[
        {'sourceUri':'proxy2.steveatgetexp.com', 'targetUri':'http://back-prod.arabidopsis.org'},
    ],
    'SubscriptionTerm':[
        {'description':'1 month', 'period':30, 'price':9.80, 'groupDiscountPercentage':10},
        {'description':'1 year', 'period':365, 'price':98, 'groupDiscountPercentage':10},
        {'description':'2 years', 'period':730, 'price':196, 'groupDiscountPercentage':10},
    ],
    'SubscriptionDescription':[
        {'header':'TAIR','descriptionType':'def'},
        {'header':'Academic Individual', 'descriptionType':'individual'},
        {'header':'Academic Institution', 'descriptionType':'institution'},
        {'header':'Commercial', 'descriptionType':'commercial'},
    ],
    'def':[
        'Unlimited access to the TAIR pages',
        'Up-to-date, manually curated data from the literature',
        'Custom datasets on request',
        'Downloadable, current genome-wide datasets',
    ],
    'individual':[
        'Low-cost access for a single researcher',
        'Discounts available when two or more researchers subscribe together',
        'Subscription cost can often be charged to your grants',
    ],
    'institution':[
        'Access for all researchers, students and staff at your institution',
        'Cost is typically covered from the library budget',
        'pricing',
    ],
    'commercial':[
        'Individual or company-wide subscription options',
        'License terms appropriate for commercial uses',
    ],
    'PaidPattern':[
        '/news/',
        '/tools/',
    ],
    'LimitValue':[
        3,
        5,
    ],
}

TEST = {
    'Partner':{
        'partnerId':'yfd',
        'name':'YFD',
        'logoUri':'https://s3-us-west-2.amazonaws.com/pw2-logo/yfd.png',
        'termOfServiceUri':'https://www.google.com/intl/en/policies/terms/?fg=1',
    },
    'PartnerPattern':[
        {'sourceUri':'https://yahoo.com', 'targetUri':'https://google.com'},
        {'sourceUri':'https://steve.com', 'targetUri':'https://azeem.com'},
    ],
    'SubscriptionTerm':[
        {'description':'Two Month', 'period':60, 'price':100, 'groupDiscountPercentage':0},
        {'description':'Eight Months', 'period':240, 'price':400, 'groupDiscountPercentage':10},
        {'description':'Three Year', 'period':1095, 'price':1800, 'groupDiscountPercentage':20},
    ],
    'SubscriptionDescription':[
        {'header':'Default for Test Partner','descriptionType':'def'},
        {'header':'Test Individual Subscription', 'descriptionType':'individual'},
        {'header':'Test Institution Subscription', 'descriptionType':'institution'},
        {'header':'Test Commercial Subscription', 'descriptionType':'commercial'},
    ],
    'def':[
        'This is default benefit #1',
        'You will be awesome',
        'You will get a million dollars',
    ],
    'individual':[
        'Somebody set up us the bomb',
        'All your base are belong to us',
        'For great justice',
    ],
    'institution':[
        'This is institution benefit #1',
        'Test',
    ],
    'commercial':[
        'This is test commercial benefit',
        'You get 50% discount',
        'Cats are awesome!',
    ],
    'PaidPattern':[
        '/paid/',
    ],
    'LimitValue':[
        5,
        10,
        15,
    ],
}

def loadItem(serializerClass, dataSet, partnerId):
    for item in dataSet:
        data = item
        data['partnerId'] = partnerId
        serializer = serializerClass(data=data)
        if serializer.is_valid():
            serializer.save()

def loadSubscriptionItem(dataSet, partnerId, subscriptionDescriptionId):
    for item in dataSet:
        data = {}
        data['partnerId'] = partnerId
        data['subscriptionDescriptionId'] = subscriptionDescriptionId
        data['text'] = item
        serializer = SubscriptionDescriptionItemSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

def loadSubscriptionDescriptionAndItem(stuff, partnerId):
    for item in stuff['SubscriptionDescription']:
        data = item
        data['partnerId'] = partnerId
        serializer = SubscriptionDescriptionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        subscriptionDescriptionId = serializer.data['subscriptionDescriptionId']
        itemDataset = stuff[item['descriptionType']]
        loadSubscriptionItem(itemDataset, partnerId, subscriptionDescriptionId) 

def loadAccessRule(paidPattern, partnerId, paidAccessTypeId):
    for item in paidPattern:
        serializer = UriPatternSerializer(data={'pattern':item})
        if serializer.is_valid():
            serializer.save()
        patternId = serializer.data['patternId']

        serializer = AccessRuleSerializer(data={
            'patternId':patternId,
            'partnerId':partnerId,
            'accessTypeId':paidAccessTypeId,
        })
        if serializer.is_valid():
            serializer.save()
        

def createPaidType():
    serializer = AccessTypeSerializer(data={'name':'Paid'})
    if serializer.is_valid():
        serializer.save()
    return serializer.data['accessTypeId']

def loadMeteringLimit(limitValues, partnerId):
    for item in limitValues:
        serializer = LimitValueSerializer(data={
            'val':item,
            'partnerId':partnerId
        })
        if serializer.is_valid():
            serializer.save()

def loadStuff(stuff, paidAccessTypeId):
    partnerId = stuff['Partner']['partnerId']
    serializer = PartnerSerializer(data=stuff['Partner'])
    if serializer.is_valid():
        serializer.save()
    else:
        print "Unable to create partner %s, exiting" % partnerId
        exit()

    loadItem(PartnerPatternSerializer, stuff['PartnerPattern'], partnerId)
    loadItem(SubscriptionTermSerializer, stuff['SubscriptionTerm'], partnerId)
    loadSubscriptionDescriptionAndItem(stuff, partnerId)

    loadAccessRule(stuff['PaidPattern'], partnerId, paidAccessTypeId)

    loadMeteringLimit(stuff['LimitValue'], partnerId)

def loadApiKey(stuff):
    for item in stuff:
        serializer = ApiKeySerializer(data=item)
        if serializer.is_valid():
            serializer.save()

loadApiKey(APIKEY)
paidAccessTypeId = createPaidType()
loadStuff(TEST, paidAccessTypeId)
loadStuff(TAIR, paidAccessTypeId)
