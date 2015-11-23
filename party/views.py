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
from rest_framework import status
from rest_framework.response import Response

from django.core.mail import send_mail
from common.permissions import isPhoenix

# top level: /parties/

# Basic CRUD operation for Party and IpRange

# /
class PartyCRUD(GenericCRUDView):
    requireApiKey = False
    queryset = Party.objects.all()
    serializer_class = PartySerializer

    def get_queryset(self):
        if isPhoenix(self.request):
            if 'partyId' in self.request.GET:
                partyId = self.request.GET.get('partyId')
                return super(PartyCRUD, self).get_queryset().filter(partyId=partyId)
            elif 'partyType' in self.request.GET:
                partyType = self.request.GET.get('partyType')
                return super(PartyCRUD, self).get_queryset().filter(partyType=partyType)
        return []
# TODO: "post" is still a security vulnerability -SC

# /ipranges/
class IpRangeCRUD(GenericCRUDView):
    requireApiKey = False
    queryset = IpRange.objects.all()
    serializer_class = IpRangeSerializer

    def get_queryset(self):
        if isPhoenix(self.request):
            partyId = self.request.GET.get('partyId')
            return super(IpRangeCRUD, self).get_queryset().filter(partyId=partyId)
        return []
# TODO: "post" is still a security vulnerability -SC

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
                                 .filter(display=True) \
                                 .filter(partyType="organization")
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

# /usage/
class Usage(APIView):
    requireApiKey = False
    def post(self, request, format=None):
        # security vulnerability: consortiumId should come from partyId in cookie that's been validated via isPhoenix -SC
        if not isPhoenix(request):
            return HttpResponse(status=400)
        data = request.data
        subject = "Institution Usage Request For %s" % (data['institution'])
        message = "Start date: %s\n" \
                  "End date: %s\n" \
                  "Comments: %s\n" \
                  % (data['startDate'], data['endDate'], data['comments'])
        from_email = "info@arabidopsis.org"
        recipient_list = ["info@arabidopsis.org"]
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
        return HttpResponse(json.dumps({'message': 'success'}), status=200)

class ConsortiumInstitutions(APIView):
    requireApiKey = False
    def get(self, request, consortiumId, format=None):
        # security vulnerability: consortiumId should come from partyId in cookie that's been validated via isPhoenix -SC
        if not isPhoenix(request):
            return HttpResponse(status=400)
	institutions = Party.objects.get(partyId=consortiumId).party_set.all()
        serializer = PartySerializer(institutions, many=True)
        ret = [dict(s) for s in serializer.data]
	#for s in serializer.data:
        #    ret_tmp = dict(s)
        #    ret_tmp['id'] = ret_tmp['partyId']
        #    ret_tmp['state'] = None
        #    ret.append(ret_tmp)
        return HttpResponse(json.dumps(ret), status=200)

# ipranges/getall/
class GetAllIpranges(GenericCRUDView):
    requireApiKey = False
    def get(self, request):
        ipRangeList = IpRange.objects.all()
        serializer = IpRangeSerializer(ipRangeList, many=True)

        if True: #TODO: return only the user is admin
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)