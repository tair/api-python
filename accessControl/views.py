#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import generics
from services import MeteringService, SubscriptionService
from controls import AccessControl

from models import AccessType, AccessRule, Pattern
from serializers import AccessTypeSerializer, AccessRuleSerializer, PatternSerializer

import json

# top level: /accessControls/


# Main API call to access control service. Caller gives in partyId, and the
# service outputs access control status such as "OK", "Warn", "BlockBySubscription".

# /access/
class Access(APIView):
    def get(self, request, format=None):
        ip = request.GET.get('ip')
        url = request.GET.get('url')
        partyId = request.GET.get('partyId')
        status = AccessControl.getAccessStatus(ip, partyId, url)
        response = {
            "status":status,
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

# /subscriptions/
class SubscriptionsAccess(APIView):
    def get(self, request, format=None):
        ip = request.GET.get('ip')
        url = request.GET.get('url')
        partyId = request.GET.get('partyId')
        access = AccessControl.subscription(ip, partyId, url)
        response = {
            "access":access,
        }
        return HttpResponse(json.dumps(response), content_type="application/json")


# Basic CRUD operation for AccessType, AccessRule, and Pattern

# /accessTypes/
class AccessTypesList(generics.ListCreateAPIView):
    queryset = AccessType.objects.all()
    serializer_class = AccessTypeSerializer

# /accessTypes/<primary-key>
class AccessTypesDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccessType.objects.all()
    serializer_class = AccessTypeSerializer

# /accessRules/
class AccessRulesList(generics.ListCreateAPIView):
    queryset = AccessRule.objects.all()
    serializer_class = AccessRuleSerializer

# /accessRules/<primary-key>
class AccessRulesDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccessRule.objects.all()
    serializer_class = AccessRuleSerializer

# /patterns/
class PatternsList(generics.ListCreateAPIView):
    queryset = Pattern.objects.all()
    serializer_class = PatternSerializer

# /patterns/<primary-key>
class PatternsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pattern.objects.all()
    serializer_class = PatternSerializer
