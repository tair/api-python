#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from party.models import Party, IpRange
from party.serializers import PartySerializer, IpRangeSerializer

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

class OrganizationCRUD(APIView):
    def get(self, request, format=None):
        obj = Party.objects.all().filter(partyType='organization')
        out = []
        for entry in obj:
            out.append(entry.name)
        return HttpResponse(json.dumps(out), content_type="application/json")
