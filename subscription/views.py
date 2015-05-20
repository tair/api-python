#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.http import HttpResponse

from subscription.models import Party, Subscription, IpRange, SubscriptionTransaction
from subscription.serializers import PartySerializer, SubscriptionSerializer, IpRangeSerializer, SubscriptionTransactionSerializer

from partner.models import Partner

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from common.views import GenericCRUDView

import json

import datetime
# top level: /subscriptions/

# Basic CRUD operation for Parties, IpRanges, Subscriptions, and SubscriptionTransactions

# /parties/
class PartyCRUD(GenericCRUDView):
    queryset = Party.objects.all()
    serializer_class = PartySerializer

# /ipranges/
class IpRangeCRUD(GenericCRUDView):
    queryset = IpRange.objects.all()
    serializer_class = IpRangeSerializer

# /
class SubscriptionCRUD(GenericCRUDView):
    def get_queryset(self):
        return Partner.getQuerySet(self, Subscription, 'partnerId')
    serializer_class = SubscriptionSerializer

    # overrides default POST to create a subscription transaction
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            subscription = serializer.save()
            transaction = SubscriptionTransaction.createFromSubscription(subscription, 'Initial')
            returnData = serializer.data
            returnData['subscriptionTransactionId']=transaction.subscriptionTransactionId
            return Response(returnData, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# /transactions/
class SubscriptionTransactionCRUD(GenericCRUDView):
    queryset = SubscriptionTransaction.objects.all()
    serializer_class = SubscriptionTransactionSerializer

#------------------- End of Basic CRUD operations --------------


# Specific queries

# /active/
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


# /<pk>/renewal/
class SubscriptionRenewal(generics.GenericAPIView):
    def get_queryset(self):
        return Partner.getQuerySet(self, Subscription, 'partnerId')
    serializer_class = SubscriptionSerializer

    def put(self, request, pk):
        subscription = Subscription.objects.get(subscriptionId=pk)
        serializer = SubscriptionSerializer(subscription, data=request.data)
        if serializer.is_valid():
            subscription = serializer.save()
            transaction = SubscriptionTransaction.createFromSubscription(subscription, 'Renewal')
            returnData = serializer.data
            returnData['subscriptionTransactionId']=transaction.subscriptionTransactionId
            return Response(returnData)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

