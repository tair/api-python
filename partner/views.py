#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import generics

from models import Partner, PartnerPattern, SubscriptionTerm
from serializers import PartnerSerializer, PartnerPatternSerializer, SubscriptionTermSerializer

import json

from rest_framework import status
from rest_framework.response import Response

# top level: /partners/


# Basic CRUD operation for Partner

# /
class PartnerList(generics.ListCreateAPIView):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer

# /<primary-key>
class PartnerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer

# /patterns
class PartnerPatternsList(generics.ListCreateAPIView):
    def get_queryset(self):
        return Partner.getQuerySet(self, PartnerPattern, 'partnerId')
    serializer_class = PartnerPatternSerializer

# /patterns/<primary-key>
class PartnerPatternsDetail(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        return Partner.getQuerySet(self, PartnerPattern, 'partnerId')
    serializer_class = PartnerPatternSerializer

# /terms/
class TermsList(generics.ListCreateAPIView):
    def get_queryset(self):
        return Partner.getQuerySet(self, SubscriptionTerm, 'partnerId')
    serializer_class = SubscriptionTermSerializer

# /terms/<primary_key>/
class TermsDetail(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        return Partner.getQuerySet(self, SubscriptionTerm, 'partnerId')
    serializer_class = SubscriptionTermSerializer


#specific queries

# /terms
class TermsQueries(APIView):
    def get(self, request, format=None):
        price = request.GET.get('price')
        period = request.GET.get('period')
        groupDiscountPercentage = request.GET.get('groupDiscountPercentage')

        obj = SubscriptionTerm.objects.all()
        if not price == None:
            obj = obj.filter(price=price)
        if not period == None:
            obj = obj.filter(period=period)
        if not groupDiscountPercentage == None:
            obj = obj.filter(groupDiscountPercentage=groupDiscountPercentage)
        obj = Partner.filters(self, obj, 'partnerId')
        serializer = SubscriptionTermSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
