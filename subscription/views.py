#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.http import HttpResponse

from subscription.models import Party, Payment, Subscription, SubscriptionIpRange, SubscriptionTerm
from subscription.serializers import PartySerializer, PaymentSerializer, SubscriptionSerializer, SubscriptionIpRangeSerializer, SubscriptionTermSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics

import json

# top level: /subscriptions/

# Basic CRUD operation for Parties, Payments, IpRanges, Terms, Subscriptions
# /parties/
class PartiesList(generics.ListCreateAPIView):
    queryset = Party.objects.all()
    serializer_class = PartySerializer

# /parties/<primary_key>
class PartiesDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Party.objects.all()
    serializer_class = PartySerializer

# /payments/
class PaymentsList(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

# /payments/<primary_key>/
class PaymentsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

# /ipranges/
class IpRangesList(generics.ListCreateAPIView):
    queryset = SubscriptionIpRange.objects.all()
    serializer_class = SubscriptionIpRangeSerializer

# /ipranges/<primary_key>/
class IpRangesDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubscriptionIpRange.objects.all()
    serializer_class = SubscriptionIpRangeSerializer

# /terms/
class TermsList(generics.ListCreateAPIView):
    queryset = SubscriptionTerm.objects.all()
    serializer_class = SubscriptionTermSerializer

# /terms/<primary_key>/
class TermsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubscriptionTerm.objects.all()
    serializer_class = SubscriptionTermSerializer

# /subscriptions/
class SubscriptionsList(generics.ListCreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

# /subscriptions/<primary_key>/
class SubscriptionsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

#------------------- End of Basic CRUD operations --------------


# Specific queries

# /subscriptions/active/
class SubscriptionsActive(APIView):
    def get(self, request, format=None):
        partyId = request.GET.get('partyId')
        ip = request.GET.get('ip')
        isActive = False
        if not partyId == None:
            isActive = Subscription.getActiveById(partyId)
        elif not ip == None:
            isActive = Subscription.getActiveByIp(ip)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return HttpResponse(json.dumps({'active':isActive}), content_type="application/json")

# /subscriptions/<primary key>/payments
class SubscriptionsPayments(APIView):
    def get(self, request, pk, format=None):
        obj = Payment.objects.filter(partyId=pk)
        serializer = PaymentSerializer(obj, many=True)
        return Response(serializer.data)

# /subscriptions/<primary key>/prices
class SubscriptionsPrices(APIView):
    def get(self, request, pk, format=None):
        obj = SubscriptionTerm.getByPartyId(pk)
        serializer = SubscriptionTermSerializer(obj, many=True)
        return Response(serializer.data)

# /terms
class TermsQueries(APIView):
    def get(self, request, format=None):
        price = request.GET.get('price')
        period = request.GET.get('period')
        autoRenew = request.GET.get('autoRenew')
        groupDiscountPercentage = request.GET.get('groupDiscountPercentage')

        obj = SubscriptionTerm.objects.all()
        if not price == None:
            obj = obj.filter(price=price)
        if not period == None:
            obj = obj.filter(period=period)
        if not autoRenew == None:
            obj = obj.filter(autoRenew=autoRenew)
        if not groupDiscountPercentage == None:
            obj = obj.filter(groupDiscountPercentage=groupDiscountPercentage)
        serializer = SubscriptionTermSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
