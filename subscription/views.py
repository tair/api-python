#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.http import HttpResponse

from subscription.models import Party, Subscription, IpRange, SubscriptionTransaction
from subscription.serializers import PartySerializer, SubscriptionSerializer, IpRangeSerializer, SubscriptionTransactionSerializer

from partner.models import Partner

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics

import json

# top level: /subscriptions/

# Basic CRUD operation for Parties, IpRanges, Subscriptions, and SubscriptionTransactions

# /parties/
class PartiesList(generics.ListCreateAPIView):
    queryset = Party.objects.all()
    serializer_class = PartySerializer

# /parties/<primary_key>
class PartiesDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Party.objects.all()
    serializer_class = PartySerializer

# /ipranges/
class IpRangesList(generics.ListCreateAPIView):
    queryset = IpRange.objects.all()
    serializer_class = IpRangeSerializer

# /ipranges/<primary_key>/
class IpRangesDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = IpRange.objects.all()
    serializer_class = IpRangeSerializer

# /subscriptions/
class SubscriptionsList(generics.ListCreateAPIView):
    def get_queryset(self):
        return Partner.getQuerySet(self, Subscription, 'partnerId')
    serializer_class = SubscriptionSerializer

# /subscriptions/<primary_key>/
class SubscriptionsDetail(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        return Partner.getQuerySet(self, Subscription, 'partnerId')
    serializer_class = SubscriptionSerializer

# /transactions/
class SubscriptionTransactionsList(generics.ListCreateAPIView):
    queryset = SubscriptionTransaction.objects.all()
    serializer_class = SubscriptionTransactionSerializer

# /transactions/<primary_key>/
class SubscriptionTransactionsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubscriptionTransaction.objects.all()
    serializer_class = SubscriptionTransactionSerializer

#------------------- End of Basic CRUD operations --------------


# Specific queries

# /subscriptions/active/
class SubscriptionsActive(APIView):
    def get(self, request, format=None):
        partyId = request.GET.get('partyId')
        ip = request.GET.get('ip')
        isActive = False
        if not partyId == None:
            obj = Subscription.getActiveById(partyId)
            obj = Partner.filters(self, obj, 'partnerId')
            isActive = len(obj) > 0
        elif not ip == None:
            objList = Subscription.getActiveByIp(ip)
            partnerId = Partner.getPartnerId(self)
            for obj in objList:
                if obj.partnerId.partnerId == partnerId:
                    isActive = True
                    break
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return HttpResponse(json.dumps({'active':isActive}), content_type="application/json")
