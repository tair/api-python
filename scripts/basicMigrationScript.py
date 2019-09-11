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
from party.serializers import PartySerializer
from authentication.serializers import CredentialSerializer

from .tairData import TAIR

APIKEY = [
    {'apiKey':'test123'},
]


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

def loadAccessRule(patterns, partnerId, accessTypeId):
    for item in patterns:
        serializer = UriPatternSerializer(data={'pattern':item})
        if serializer.is_valid():
            serializer.save()
        patternId = serializer.data['patternId']

        serializer = AccessRuleSerializer(data={
            'patternId':patternId,
            'partnerId':partnerId,
            'accessTypeId':accessTypeId,
        })
        if serializer.is_valid():
            serializer.save()

def createPaidType():
    serializer = AccessTypeSerializer(data={'name':'Paid'})
    if serializer.is_valid():
        serializer.save()
    return serializer.data['accessTypeId']

def createLoginType():
    serializer = AccessTypeSerializer(data={'name':'Login'})
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

def loadTestUser(testUsers, partnerId):
    for item in testUsers:
        serializer = PartySerializer(data={'partyType':'user'})
        if serializer.is_valid():
            serializer.save()
        partyId= serializer.data['partyId']
        serializer = CredentialSerializer(data={
            'username':item['username'],
            'password':item['password'],
            'email':item['email'],
            'institution':item['institution'],
            'userIdentifier':item['userIdentifier'],
            'partyId':partyId,
            'partnerId':partnerId,
        })
        if serializer.is_valid():
            serializer.save()

def loadPartner(partner, paidAccessTypeId, loginAccessTypeId):
    partnerId = partner['Partner']['partnerId']
    serializer = PartnerSerializer(data=partner['Partner'])
    if serializer.is_valid():
        serializer.save()
    else:
        print("Unable to create partner %s, exiting" % partnerId)
        exit()

    loadItem(PartnerPatternSerializer, partner['PartnerPattern'], partnerId)
    loadItem(SubscriptionTermSerializer, partner['SubscriptionTerm'], partnerId)
    loadSubscriptionDescriptionAndItem(partner, partnerId)
    loadAccessRule(partner['PaidPattern'], partnerId, paidAccessTypeId)
    loadAccessRule(partner['LoginPattern'], partnerId, loginAccessTypeId)
    loadMeteringLimit(partner['LimitValue'], partnerId)
    loadTestUser(partner['TestUser'], partnerId)

def loadApiKey(apiKeys):
    for item in apiKeys:
        serializer = ApiKeySerializer(data=item)
        if serializer.is_valid():
            serializer.save()

loadApiKey(APIKEY)
paidAccessTypeId = createPaidType()
loginAccessTypeId = createLoginType()
loadPartner(TAIR, paidAccessTypeId, loginAccessTypeId)
