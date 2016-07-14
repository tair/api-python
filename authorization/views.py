#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import generics
from controls import Authorization

from models import AccessType, AccessRule, UriPattern
from serializers import AccessTypeSerializer, AccessRuleSerializer, UriPatternSerializer
from partner.models import Partner
from authentication.models import Credential
from common.views import GenericCRUDView

from rest_framework.response import Response
from rest_framework import status

import json
import re
import urllib

# top level: /authorizations/


# Main API call to access control service. Caller gives in partyId, and the
# service outputs access control status such as "OK", "Warn", "BlockBySubscription".

# /access/
class Access(APIView):
    def get(self, request, format=None):
        partyId = request.COOKIES.get('credentialId')
        loginKey = request.COOKIES.get('secretKey')
        ip = request.GET.get('ip')
        url = request.GET.get('url').decode('utf8')
        partnerId = request.GET.get('partnerId')
        apiKey = request.COOKIES.get('apiKey')

        status = Authorization.getAccessStatus(loginKey, ip, partyId, url, partnerId, getHostUrlFromRequest(request), apiKey)        
        userIdentifier = None
        if partyId and partyId.isdigit() and Credential.objects.all().filter(partyId=partyId).exists():
            userIdentifier = Credential.objects.all().get(partyId=partyId).userIdentifier
        response = {
            "status":status,
            "userIdentifier":userIdentifier,
        }

        return HttpResponse(json.dumps(response), content_type="application/json")

# /subscriptions/
class SubscriptionsAccess(APIView):
    def get(self, request, format=None):
        ip = request.GET.get('ip')
        url = request.GET.get('url')
        partyId = request.GET.get('partyId')
        partnerId = request.GET.get('partnerId')
        apiKey = request.COOKIES.get('apiKey')
        access = Authorization.subscription(ip, partyId, url, partnerId, getHostUrlFromRequest(request), apiKey)
        response = {
            "access":access,
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

# /authentications/
class AuthenticationsAccess(APIView):
    def get(self, request, format=None):
        credentialId = request.COOKIES.get('credentialId')
        loginKey = request.COOKIES.get('secretKey')
        url = request.GET.get('url')
        partnerId = request.GET.get('partnerId')
        hostUrl = "http://%s" % request.get_host()
        apiKey = request.COOKIES.get('apiKey')
        access = Authorization.authentication(loginKey, credentialId, url, partnerId, getHostUrlFromRequest(request), apiKey)
        response = {
            "access":access,
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

class URIAccess(APIView):
    
    def put(self, request, format=None):
        params = request.GET
        if 'patternId' not in params:
            return Response({'error': 'Put method needs patternId'}, status=status.HTTP_400_BAD_REQUEST)
        patternIdFromRequest = request.GET.get('patternId') #URL PARAM
        patternFromRequest = request.data['pattern'] #FORM DATA/BODY
        pattern = UriPattern.objects.get(patternId=patternIdFromRequest)
        serializer = UriPatternSerializer(pattern,data=patternFromRequest)
        if serializer.is_valid():
            pattern.save();
            returnData = serializer.data
            return Response(returnData, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self,request, format=None):
        #data = request.data.copy()
        dataFromRequest = request.data
        patternFromRequest = request.data['pattern']
        serializer = UriPatternSerializer(data=dataFromRequest)
        isREValid = isRegExpValid(patternFromRequest)
        
        if serializer.is_valid():
            
            if isREValid:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'error':'RE invalid'}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Basic CRUD operation for AccessType, AccessRule, and UriPattern

# /accessTypes/
class AccessTypeCRUD(GenericCRUDView):
    queryset = AccessType.objects.all()
    serializer_class = AccessTypeSerializer

# /accessRules/
class AccessRuleCRUD(GenericCRUDView):
    queryset = AccessRule.objects.all()
    serializer_class = AccessRuleSerializer

# /patterns/
class UriPatternCRUD(GenericCRUDView):
    queryset = UriPattern.objects.all()
    serializer_class = UriPatternSerializer

# Utility functions

def getHostUrlFromRequest(request):
    if (request.is_secure()):
        protocol = 'https'
    else:
        protocol = 'http'
    return "%s://%s" % (protocol, request.get_host())

def isRegExpValid(inString):
    try:
        re.compile(inString)
        is_valid = True
    except re.error:
        is_valid = False
    return is_valid
