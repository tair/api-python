#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import generics

from models import Partner, PartnerPattern, SubscriptionTerm
from serializers import PartnerSerializer, PartnerPatternSerializer, SubscriptionTermSerializer

import json

from common.views import GenericCRUDView

from rest_framework import status
from rest_framework.response import Response

# top level: /partners/


# Basic CRUD operation for Partner

# /
class PartnerCRUD(GenericCRUDView):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer

    def get(self, request, format=None):
        obj = self.get_queryset()
        params = request.GET
        if 'uri' in params:
            obj = obj.extra(
                tables=["PartnerPattern"],
                where=["Partner.partnerId=PartnerPattern.partnerId", "PartnerPattern.pattern=%s"],
                params=[params['uri']]
            )
        serializer = self.serializer_class(obj, many=True)
        return Response(serializer.data)

# /patterns
class PartnerPatternCRUD(GenericCRUDView):
    queryset = PartnerPattern.objects.all()
    serializer_class = PartnerPatternSerializer

# /terms/
class TermsCRUD(GenericCRUDView):
    queryset = SubscriptionTerm.objects.all()
    serializer_class = SubscriptionTermSerializer

# specific api calls

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
        serializer = SubscriptionTermSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
