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

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)
'''
authorization  access  should contain these elements:

timestamp (current date and time, required) +
IP address (required) +
party id (may be null) +
user identifier (may be null) 
partner id (required) 
complete URI (required) 
status (required) 
'''

# top level: /authorizations/


# Main API call to access control service. Caller gives in partyId, and the
# service outputs access control status such as "OK", "Warn", "BlockBySubscription".

# /access/
    
class Access(APIView):
    #another way w/o LOGGING in settings.py
    #import os
    #dirname = os.path.dirname(os.path.realpath(__file__))
    #logging.basicConfig(filename="%s/logs/authorization_access.log" % dirname,
    #                    format='%(asctime)s %(message)s')
    
    def get(self, request, format=None):
        
        partyId = request.COOKIES.get('credentialId')
        logging.info("%s, %s" % (partyId, "PARTYID"))
        
        loginKey = request.COOKIES.get('secretKey')
        
        ip = request.GET.get('ip')
        logging.info("%s, %s" % (ip, "ip"))
        
        url = request.GET.get('url').decode('utf8')
        logging.info("%s, %s" % (url, "url"))
        
        partnerId = request.GET.get('partnerId')
        logging.info("%s, %s" % (partnerId, "partnerId"))
        
        apiKey = request.COOKIES.get('apiKey')

        status = Authorization.getAccessStatus(loginKey, ip, partyId, url, partnerId, getHostUrlFromRequest(request), apiKey)
        logging.info("%s, %s" % (status, "status"))
             
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
    def get(self, request, format=None):
        params = request.GET
        if 'patternId' not in params:
            obj = UriPattern.objects.all()
            serializer = UriPatternSerializer(obj, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            #requestPatternId = params['patternId']
            requestPatternId = request.GET.get('patternId')
            if UriPattern.objects.filter(patternId = requestPatternId).exists():
                obj = UriPattern.objects.get(patternId = requestPatternId)
                serializer = UriPatternSerializer(obj, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'GET error: patternId' + requestPatternId + ' not found'})
        
    def delete(self, request, format=None):
       params = request.GET
       if 'patternId' not in params:
           return Response({'DELETE error':'patternId required'},status=status.HTTP_400_BAD_REQUEST)
        
       requestPatternId = params['patternId']
       if UriPattern.objects.filter(patternId = requestPatternId).exists():
           pattern = UriPattern.objects.get(patternId = requestPatternId)
           pattern.delete()
           return Response({'DELETE success':'delete of patternId '+requestPatternId+' completed'},status=status.HTTP_200_OK)
       else:
           return Response({'DELETE error':'delete of patternId '+requestPatternId+' failed. patternId not found'},status=status.HTTP_400_BAD_REQUEST)
          
    def put(self, request, format=None):
        params = request.GET
        if 'patternId' not in params:
            return Response({'error': 'PUT method:patternId is required as URL parameter'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        if 'pattern' not in data:
            return Response({'error':'PUT method:pattern is required as form-data'}, status=status.HTTP_400_BAD_REQUEST)
        
        patternFromRequest = data['pattern']
        isREValid = isRegExpValid(patternFromRequest)
        if not isREValid:
            return Response({'error':'PUT method:pattern '+patternFromRequest+' is not valid regexp'}, status=status.HTTP_400_BAD_REQUEST)

        patternIdFromRequest = request.GET.get('patternId')
        if not UriPattern.objects.filter(patternId = patternIdFromRequest).exists():
            return Response({'error':'PUT method:patternId '+patternIdFromRequest+' not found'}, status=status.HTTP_400_BAD_REQUEST)
              
        pattern = UriPattern.objects.get(patternId=patternIdFromRequest)
        serializer = UriPatternSerializer(pattern,data=data)

        if serializer.is_valid():
            serializer.save();
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self,request, format=None):
        data = request.data
        if 'pattern' not in data:
            return Response({'error':'POST method:pattern is required as form-data'}, status=status.HTTP_400_BAD_REQUEST)
        
        patternFromRequest = data['pattern']
        isREValid = isRegExpValid(patternFromRequest)
        if not isREValid:
            return Response({'error':'POST method:pattern '+patternFromRequest+' is not valid regexp'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UriPatternSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
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
    if not inString:
        return False
    try:
        re.compile(inString)
        is_valid = True
    except re.error:
        is_valid = False
    return is_valid
