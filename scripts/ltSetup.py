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


def loadTestUser(testUsers):
    partnerId = 'phoenix'
    for item in testUsers:
        serializer = CredentialSerializer(data={
            'username':item['username'],
            'password':item['password'],
            'email':item['email'],
            'institution':item['institution'],
            'userIdentifier':item['userIdentifier'],
            'partyId':item['partyId'],
            'partnerId':partnerId,
        })
        if serializer.is_valid():
            serializer.save()

testUsers = [
    {
        'username':'steveStaff',
        'password':'stevepass',
        'email':'steve@getexp.com',
        'institution':'getexp',
        'userIdentifier':'00000001',
        'partyId':42,
    }
]

testConsortium = [
    {
        'name':'UC consortium',
        'countryId':117,
        'institutions':[
            55,
            56,
            57,
            58
        ]
    },
    {
        'name':'Unbelievable Consortium',
        'countryId':117,
        'institutions':[
            718,
            604,
        ]
    }
]

def loadTestConsortium(testConsortium):
    for item in testConsortium:
        serializer = PartySerializer(data={
            'partyType':'consortium',
            'name':item['name'],
            'display':1,
            'countryId':item['countryId'],
            'consortium_id':None,
        })
        if serializer.is_valid():
            serializer.save()

#loadTestUser(testUsers)
#loadTestConsortium(testConsortium)
