#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import generics

from .models import Partner, PartnerPattern, SubscriptionTerm, SubscriptionDescription, SubscriptionDescriptionItem
from .serializers import PartnerSerializer, PartnerPatternSerializer, SubscriptionTermSerializer, SubscriptionDescriptionSerializer, SubscriptionDescriptionItemSerializer

import json

from common.views import GenericCRUDView

from rest_framework import status
from rest_framework.response import Response

import re

# top level: /partners/


# Basic CRUD operation for Partner

# /
class PartnerCRUD(GenericCRUDView):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    requireApiKey = False

    def get(self, request, format=None):
        obj = self.get_queryset()
        params = request.GET
        if request.GET.get('authority')=='admin':
            partnerList = Partner.objects.all()
            serializer = PartnerSerializer(partnerList, many=True)
            return Response(serializer.data)
        serializer = self.serializer_class(obj, many=True)
        return Response(serializer.data)

    def post(self, request):
        return Response({'msg':'cannot create'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        return Response({'msg':'cannot update'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        return Response({'msg':'cannot delete'}, status=status.HTTP_400_BAD_REQUEST)

# /patterns
class PartnerPatternCRUD(GenericCRUDView):
    queryset = PartnerPattern.objects.all()
    serializer_class = PartnerPatternSerializer
    requireApiKey = False

    def get(self, request, format=None):
        params = request.GET
        if 'sourceUri' not in params:
            return Response({'error':'sourceUri field is required'}, status=status.HTTP_400_BAD_REQUEST)
        partnerList = []
        serializer = self.serializer_class(PartnerPattern.objects.all().order_by('partnerPatternId'), many=True)
        for url in serializer.data:
            pattern = re.compile(url['sourceUri'])
            if pattern.search(params['sourceUri']):
                partnerList.append(url)
                return Response(partnerList)
        # serializer = PartnerPatternSerializer(partnerList, many=True)
        return Response({'msg':'cannot find matched url'}, status=status.HTTP_204_NO_CONTENT)

# /terms/
class TermsCRUD(GenericCRUDView):
    queryset = SubscriptionTerm.objects.all()
    serializer_class = SubscriptionTermSerializer
    requireApiKey = False

    def post(self, request):
        return Response({'msg':'cannot create'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        return Response({'msg':'cannot update'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        return Response({'msg':'cannot delete'}, status=status.HTTP_400_BAD_REQUEST)

# /descriptions/
class SubscriptionDescriptionCRUD(GenericCRUDView):
    queryset = SubscriptionDescription.objects.all()
    serializer_class = SubscriptionDescriptionSerializer
    requireApiKey = False

    def get(self, request, format=None):
        obj = self.get_queryset()
        params = request.GET
        if 'includeText' in params and params['includeText'] and 'partnerId' in params:
            out = {}
            for entry in obj:
                outEntry = {}
                outEntry['id'] = entry.descriptionType
                outEntry['heading'] = entry.header
                subscriptionDescriptionId = entry.subscriptionDescriptionId
                itemObj = SubscriptionDescriptionItem.objects.filter(subscriptionDescriptionId=subscriptionDescriptionId)
                outEntry['benefits'] = []
                for itemEntry in itemObj:
                    outEntry['benefits'].append(itemEntry.text)
                out[outEntry['id']] = outEntry
            return Response(out)
        serializer = self.serializer_class(obj, many=True)
        return Response(serializer.data)

    def post(self, request):
        return Response({'msg':'cannot create'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        return Response({'msg':'cannot update'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        return Response({'msg':'cannot delete'}, status=status.HTTP_400_BAD_REQUEST)

# /descriptionItems/
class SubscriptionDescriptionItemCRUD(GenericCRUDView):
    queryset = SubscriptionDescriptionItem.objects.all()
    serializer_class = SubscriptionDescriptionItemSerializer

