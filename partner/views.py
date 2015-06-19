#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import generics

from models import Partner, PartnerPattern, SubscriptionTerm, SubscriptionDescription, SubscriptionDescriptionItem
from serializers import PartnerSerializer, PartnerPatternSerializer, SubscriptionTermSerializer, SubscriptionDescriptionSerializer, SubscriptionDescriptionItemSerializer

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
            patternObj = PartnerPattern.objects.filter(sourceUri=params['uri'])
            serializer = PartnerPatternSerializer(patternObj, many=True)
            return Response(serializer.data)
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

# /descriptionItems/
class SubscriptionDescriptionItemCRUD(GenericCRUDView):
    queryset = SubscriptionDescriptionItem.objects.all()
    serializer_class = SubscriptionDescriptionItemSerializer
    requireApiKey = False
