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
from authentication.serializers import UserSerializer

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
        {'header':'Subscription Benefit','descriptionType':'def'},
        {'header':'Individual Subscription Benefit', 'descriptionType':'individual'},
        {'header':'Institution Subscription Benefit', 'descriptionType':'institution'},
        {'header':'Commercial Subscription Benefit', 'descriptionType':'commercial'},
    ],
    'def':[
        'Unlimited access to the TAIR pages',
        'Up-to-date, manually curated data from the literature',
        'Custom datasets on request',
        'Downloadable, current genome-wide datasets',
    ],
    'individual':[
        'Access for a single research',
        'Each lab member requires their own individual subscription',
        'Discounts available when two or more individuals subscribe together',
    ],
    'institution':[
        'Unlimited access for all researchers, students and staff at your institution',
        'Cost is typically covered by your library',
        'Access is granted automatically by IP address',
    ],
    'commercial':[
        'Used by most top agroscience companies',
        'Subscription options for entire companies or individual commercial uses',
        'License terms appropriate for commercial uses',
    ],
    'PaidPattern':[
        '/servlet/TairObject\?((id=\d+\&type=assignment)|(type=assignment\&id=\d+))',
        '/servlet/TairObject\?((id=\d+\&type=gene)|(type=gene\&id=\d+))',
        '/servlet/TairObject\?((id=\d+\&type=assemblyunit)|(type=assemblyunit\&id=\d+))',
        '/servlet/TairObject\?((id=\d+\&type=marker)|(type=marker\&id=\d+))',
        '/servlet/TairObject\?((id=\d+\&type=locus)|(type=locus\&id=\d+))',
        '/servlet/TairObject\?((id=\d+\&type=contig)|(type=contig\&id=\d+))',
        '/servlet/TairObject\?((id=\d+\&type=cloneend)|(type=cloneend\&id=\d+))',
        '/servlet/TairObject\?((id=\d+\&type=polyallele)|(type=polyallele\&id=\d+))',
        '/servlet/TairObject\?((id=\d+\&type=restrictionenzyme)|(type=restrictionenzyme\&id=\d+))',
        '/servlet/TairObject\?((id=\d+\&type=sequence)|(type=sequence\&id=\d+))',
        '/servlet/TairObject\?((id=\d+\&type=species_variant)|(type=species_variant\&id=\d+))',
        '/servlet/TairObject\?((id=\d+\&type=host_strain)|(type=host_strain\&id=\d+))',
        '/servlet/TairObject\?((id=\d+\&type=keyword)|(type=keyword\&id=\d+))',
        '/servlets/Search.*type=annotation',
        '/servlets/tools/',
        '/servlets/mapper',
        '/biocyc/index.jsp',
        '/tools/nbrowse.jsp',
        '/tools/igb/91',
        '/Blast/',
        '/wublast/',
        '/fasta/',
        '/ChromosomeMap/',
        '/portals/masc/',
        '/portals/mutants/',
        '/portals/proteome/',
        '/portals/metabolome/',
        '/download/index-auto.jsp/?(!?dir=/download_files/Protocols)',
        '/submit/ExternalLinkSubmission.jsp',
        '/submit/genefamily_submission.jsp',
        '/submit/gene_annotation.submission.jsp',
        '/submit/marker_submission.jsp',
        '/submit/pathway_submission.jsp',
        '/submit/phenotype_submission.jsp',
        '/submit/protocol_submission.jsp',
        '/submit/submit_2010.jsp',
        '/news/newsgroup.jsp',
        '/news/newsletter_archive.jsp',
        '/news/events.jsp',
        '/news/jobs.jsp',
    ],
    'LimitValue':[
        3,
        5,
    ],
    'TestUser':[
        {'username':'stevetest', 'password':'stevepass', 'email':'steve@getexp.com', 'institution':'getexp', 'userIdentifier':'steve'},
        {'username':'azeemtest', 'password':'azeempass', 'email':'azeem@getexp.com', 'institution':'getexp', 'userIdentifier':'azeem'},
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
        {'sourceUri':'testyfd.com', 'targetUri':'http://back-prod.testyfd.com'},
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
    'TestUser':[
        {'username':'stevetest', 'password':'stevepass', 'email':'steve@getexp.com', 'institution':'getexp', 'userIdentifier':'steve'},
        {'username':'azeemtest', 'password':'azeempass', 'email':'azeem@getexp.com', 'institution':'getexp', 'userIdentifier':'azeem'},
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

def loadTestUser(testUsers, partnerId):
    for item in testUsers:
        serializer = PartySerializer(data={'partyType':'user'})
        if serializer.is_valid():
            serializer.save()
        partyId= serializer.data['partyId']
        serializer = UserSerializer(data={
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

def loadPartner(partner, paidAccessTypeId):
    partnerId = partner['Partner']['partnerId']
    serializer = PartnerSerializer(data=partner['Partner'])
    if serializer.is_valid():
        serializer.save()
    else:
        print "Unable to create partner %s, exiting" % partnerId
        exit()

    loadItem(PartnerPatternSerializer, partner['PartnerPattern'], partnerId)
    loadItem(SubscriptionTermSerializer, partner['SubscriptionTerm'], partnerId)
    loadSubscriptionDescriptionAndItem(partner, partnerId)
    loadAccessRule(partner['PaidPattern'], partnerId, paidAccessTypeId)
    loadMeteringLimit(partner['LimitValue'], partnerId)
    loadTestUser(partner['TestUser'], partnerId)

def loadApiKey(apiKeys):
    for item in apiKeys:
        serializer = ApiKeySerializer(data=item)
        if serializer.is_valid():
            serializer.save()

loadApiKey(APIKEY)
paidAccessTypeId = createPaidType()
loadPartner(TEST, paidAccessTypeId)
loadPartner(TAIR, paidAccessTypeId)
