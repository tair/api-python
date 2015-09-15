#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from party.models import Party, IpRange, Country
from party.serializers import PartySerializer, IpRangeSerializer
from subscription.models import Subscription
from partner.models import Partner

from common.views import GenericCRUDView

from authentication.models import Credential

import json
from django.http import HttpResponse
from rest_framework.views import APIView

# top level: /parties/

# Basic CRUD operation for Party and IpRange

# /
class PartyCRUD(GenericCRUDView):
    requireApiKey = False
    queryset = Party.objects.all()
    serializer_class = PartySerializer

    def get_queryset(self):
        partyId = self.request.GET.get('partyId')
        secretKey = self.request.GET.get('secret_key')
        if partyId and secretKey and Credential.validate(partyId, secretKey):
            return super(PartyCRUD, self).get_queryset().filter(partyId=partyId)
        return []

# /ipranges/
class IpRangeCRUD(GenericCRUDView):
    requireApiKey = False
    queryset = IpRange.objects.all()
    serializer_class = IpRangeSerializer

    def get_queryset(self):
        partyId = self.request.GET.get('partyId')
        secretKey = self.request.GET.get('secret_key')
        if partyId and secretKey and Credential.validate(partyId, secretKey):
            return super(IpRangeCRUD, self).get_queryset().filter(partyId=partyId)
        return []

#------------------- End of Basic CRUD operations --------------

class OrganizationView(APIView):
    requireApiKey = False
    def get(self, request, format=None):
        partnerId = request.GET.get('partnerId')
        if not Partner.objects.all().filter(partnerId=partnerId).exists():
            return HttpResponse(json.dumps([]), content_type="application/json")

        partyList = []
        objs = Subscription.objects.all().filter(partnerId=partnerId).values('partyId')
        for entry in objs:
            partyList.append(entry['partyId'])
        obj = Party.objects.all().filter(partyId__in=partyList) \
                                 .filter(display=True)
        out = []
        for entry in obj:
            out.append((entry.name, entry.country.name))
        return HttpResponse(json.dumps(out), content_type="application/json")

class CountryView(APIView):
    requireApiKey = False
    def get(self, request, format=None):
        obj = Country.objects.all()
        out = []
        for entry in obj:
            out.append(entry.name)
        return HttpResponse(json.dumps(out), content_type="application/json")
