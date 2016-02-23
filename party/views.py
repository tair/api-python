#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from party.models import Party, IpRange, Country, PartyAffiliation
from party.serializers import PartySerializer, IpRangeSerializer
from subscription.models import Subscription
from partner.models import Partner
from django.db.models import Q

from common.views import GenericCRUDView

from authentication.models import Credential

import json
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from django.core.mail import send_mail
from common.permissions import isPhoenix

from common.permissions import ApiKeyPermission
import hashlib
from authentication.serializers import CredentialSerializer
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

# consortiums/
class ConsortiumCRUD(GenericCRUDView):
    requireApiKey = False
    queryset = Party.objects.all()
    serializer_class = PartySerializer

    def get_queryset(self):
        if isPhoenix(self.request):
            if 'partyId' in self.request.GET:
                partyId = self.request.GET.get('partyId')
                return super(ConsortiumCRUD, self).get_queryset().get(partyId=partyId)
        return []

    #Actually when we use PartyCRUD's get function we can always get consortiums list
    def get(self, request, format=None):
        serializer_class = self.get_serializer_class()
        params = request.GET
        # does not allow user to update everything, too dangerous
        if not params:
            return Response({'error':'does not allow update without query parameters'})
        obj = self.get_queryset()
        out = []
        for entry in obj.consortiums.all():
            serializer = serializer_class(entry)
            out.append(serializer.data)
        return HttpResponse(json.dumps(out), content_type="application/json")

    def put(self, request, format=None):
        serializer_class = self.get_serializer_class()
        params = request.GET
        # does not allow user to update everything, too dangerous
        if not params:
            return Response({'error':'does not allow update without query parameters'})
        obj = self.get_queryset()
        if 'consortiumId' in request.data:
            consortiumId = request.data['consortiumId']
            consortium = Party.objects.get(partyId = consortiumId)
        if 'action' in request.data:
            if request.data['action'] == 'add':
                PartyAffiliation.objects.create(childPartyId=obj, parentPartyId=consortium)
            elif request.data['action'] == 'remove':
                PartyAffiliation.objects.filter(childPartyId=obj, parentPartyId=consortium).delete()
        serializer = serializer_class(obj)
        return Response(serializer.data)

# TODO: "post" is still a security vulnerability -SC

# institutions/
#PW-161 /parties/institutions/ get all parties by partyId
class InstitutionCRUD(GenericCRUDView):
    requireApiKey = False
    queryset = Party.objects.all()
    serializer_class = PartySerializer

    def get_queryset(self):
        if isPhoenix(self.request):
            if 'partyId' in self.request.GET:
                partyId = self.request.GET.get('partyId')
                return super(InstitutionCRUD, self).get_queryset().get(partyId=partyId)
        return []

    def get(self, request, format=None):
        serializer_class = self.get_serializer_class()
        params = request.GET

        if not params:
            return Response({'error':'does not allow update without query parameters'},status=status.HTTP_400_BAD_REQUEST)
        
        obj = self.get_queryset()
        out = []
        for entry in obj.institutions.all():
            serializer = serializer_class(entry)
            out.append(serializer.data)
        return HttpResponse(json.dumps(out), content_type="application/json")

    def put(self, request, format=None):
        serializer_class = self.get_serializer_class()
        params = request.GET
        if not params:
            return Response({'error':'does not allow update without query parameters'},status=status.HTTP_400_BAD_REQUEST)
        obj = self.get_queryset()
        
        if 'institutionId' in request.data:
            institutionId = request.data['institutionId']
            consortium = Party.objects.get(partyId = institutionId)

        serializer = serializer_class(obj)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        if ApiKeyPermission.has_permission(request, self):
            data = request.data
            data['password'] = hashlib.sha1(data['password']).hexdigest()
            partySerializer = PartySerializer(data=data)
            if partySerializer.is_valid():
                partySerializer.save()
                data['partyId'] = partySerializer.data['partyId']
                credentialSerializer = CredentialSerializer(data=data)
                if credentialSerializer.is_valid():
                    credentialSerializer.save()
                    return Response(credentialSerializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(credentialSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(partySerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(partySerializer.data, status=status.HTTP_401_UNAUTHORIZED)

# affiliations/
class AffiliationCRUD(GenericCRUDView):
    requireApiKey = False
    queryset = Party.objects.all()
    serializer_class = PartySerializer

    def get_queryset(self):
        if isPhoenix(self.request):
            if 'partyId' in self.request.GET:
                partyId = self.request.GET.get('partyId')
                return super(AffiliationCRUD, self).get_queryset().get(partyId=partyId)
        return []

    def get(self, request, format=None):
       serializer_class = self.get_serializer_class()
       params = request.GET
       if not params['partyId']:
           return Response({'error':'does not allow get without partyId'})
       if not params['partyType']:
           return Response({'error':'does not allow get without partyType'})
       obj = self.get_queryset()
       out = []
       if params['partyType'] == 'consortium':
           for entry in obj.PartyAffiliation.all():
               serializer = serializer_class(entry)
               out.append(serializer.data)
       elif params['partyType'] == 'organization':
           for entry in obj.consortiums.all():
               serializer = serializer_class(entry)
               out.append(serializer.data)
       else:
           return Response({'error':'invalid partyType'})
       return HttpResponse(json.dumps(out), content_type="application/json")

    def post(self, request, format=None):
       if not isPhoenix(self.request):
           return HttpResponse(status=400)
       serializer_class = self.get_serializer_class()
       params = request.data
       if not params['parentPartyId'] or not params['childPartyId']:
           return Response({'error':'does not allow creation without query parameters'})
       parentPartyId = params['parentPartyId']
       childPartyId = params['childPartyId']
       parentParty = Party.objects.all().get(partyId=parentPartyId)
       childParty=Party.objects.all().get(partyId=childPartyId)
       PartyAffiliation.objects.create(childPartyId=childParty,parentPartyId=parentParty)
       serializer = serializer_class(childParty)
       return Response(serializer.data)

    def delete(self, request, format=None):
       if not isPhoenix(self.request):
           return HttpResponse(status=400)
       serializer_class = self.get_serializer_class()
       params = request.data
       if not params['parentPartyId'] or not params['childPartyId']:
           return Response({'error':'does not allow deletion without query parameters'})
       parentPartyId = params['parentPartyId']
       childPartyId = params['childPartyId']
       parentParty = Party.objects.all().get(partyId=parentPartyId)
       childParty=Party.objects.all().get(partyId=childPartyId)
       PartyAffiliation.objects.filter(childPartyId=childParty, parentPartyId=parentParty).delete()
       serializer = serializer_class(childParty)
       return Response(serializer.data)
# TODO: "post" is still a security vulnerability -SC
