#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import generics
from services import MeteringService, SubscriptionService
from controls import Authorization

from models import AccessType, AccessRule, UriPattern
from serializers import AccessTypeSerializer, AccessRuleSerializer, UriPatternSerializer
from partner.models import Partner
from common.views import GenericCRUDView

import json

# top level: /authorizations/


# Main API call to access control service. Caller gives in partyId, and the
# service outputs access control status such as "OK", "Warn", "BlockBySubscription".

# /access/
class Access(APIView):
    def get(self, request, format=None):
        ip = request.GET.get('ip')
        url = request.GET.get('url')
        partyId = request.GET.get('partyId')
        partnerId = request.GET.get('partnerId')
        status = Authorization.getAccessStatus(ip, partyId, url, partnerId)
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
        partnerId = request.GET.get('partnerId')
        access = Authorization.subscription(ip, partyId, url, partnerId)
        response = {
            "access":access,
        }
        return HttpResponse(json.dumps(response), content_type="application/json")


# Basic CRUD operation for AccessType, AccessRule, and UriPattern

# /accessTypes/
class AccessTypeCRUD(GenericCRUDView):
    queryset = AccessType.objects.all()
    serializer_class = AccessTypeSerializer

# /accessRules/
class AccessRuleCRUD(GenericCRUDView):
    def get_queryset(self):
        return Partner.getQuerySet(self, AccessRule, 'partnerId')
    serializer_class = AccessRuleSerializer

# /patterns/
class UriPatternCRUD(GenericCRUDView):
    queryset = UriPattern.objects.all()
    serializer_class = UriPatternSerializer
