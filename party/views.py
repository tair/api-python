#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from party.models import Party, IpRange, Country
from party.serializers import PartySerializer, IpRangeSerializer
from subscription.models import Subscription
from partner.models import Partner

from common.views import GenericCRUDView

import json
from django.http import HttpResponse
from rest_framework.views import APIView

# top level: /parties/

# Basic CRUD operation for Party and IpRange

# /
class PartyCRUD(GenericCRUDView):
    queryset = Party.objects.all()
    serializer_class = PartySerializer

# /ipranges/
class IpRangeCRUD(GenericCRUDView):
    queryset = IpRange.objects.all()
    serializer_class = IpRangeSerializer


#------------------- End of Basic CRUD operations --------------

class OrganizationView(APIView):
    def get(self, request, format=None):
        partnerId = request.GET.get('partnerId')
        if not Partner.objects.all().filter(partnerId=partnerId).exists():
            return HttpResponse(json.dumps([]), content_type="application/json")

        partyList = []
        objs = Subscription.objects.all().filter(partnerId=partnerId).values('partyId')
        for entry in objs:
            partyList.append(entry['partyId'])
        obj = Party.objects.all().filter(partyId__in=partyList)
        out = []
        for entry in obj:
            out.append(entry.name)
        return HttpResponse(json.dumps(out), content_type="application/json")

class CountryView(APIView):
    def get(self, request, format=None):
        obj = Country.objects.all()
        out = []
        for entry in obj:
            out.append(entry.name)
        return HttpResponse(json.dumps(out), content_type="application/json")
