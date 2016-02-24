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
from authentication.serializers import CredentialSerializer, CredentialSerializerNoPassword
from genericpath import exists
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

#PW-161 /parties/institutions/
#GET https://demoapi.arabidopsis.org/parties/institutions?partyId=30740&credentialId=2&secretKey=7DgskfEF7jeRGn1h%2B5iDCpvIkRA%3D
#[{"partyId": 30740, "partyType": "organization", "name": "ASPB Conference", "country": null, "display": false, "consortiums": []}]
class InstitutionCRUD(GenericCRUDView):
    requireApiKey = False
    queryset = Party.objects.all()
    serializer_class = PartySerializer

    def get_queryset(self):
        if isPhoenix(self.request):
            if 'partyId' in self.request.GET:
                partyId = self.request.GET.get('partyId')
                return super(InstitutionCRUD, self).get_queryset().filter(partyId=partyId).filter(partyType="organization")
        return []
    
    #PW-161 PUT https://demoapi.arabidopsis.org/parties/institutions?credentialId=2&secretKey=7DgskfEF7jeRGn1h%2B5iDCpvIkRA%3D
    #FORM DATA partyId is required. If pwd passed it will be updated in Credential if not - not.
    # output data from both tables for a given partyId (aka institutionId)
    def put(self, request, format=None):
        if not isPhoenix(request):
           return HttpResponse({'error':'does not allow update without credentialId and secretKey query parameters'},status=status.HTTP_400_BAD_REQUEST)
        
        params = request.GET
        data = request.data
        
        if not params:
            return Response({'error':'does not allow update without query parameters'},status=status.HTTP_400_BAD_REQUEST)
        
        if 'partyId' not in request.data:
            return Response({'error':'partyId (aka institutionId) required'},status=status.HTTP_400_BAD_REQUEST)
        
        institutionId = request.data['partyId']
        #get party
        party = Party.objects.get(partyId = institutionId)
        partySerializer = PartySerializer(party, data=data)
        
        #get credential
        credential = Credential.objects.get(partyId = institutionId)
        
        if 'password' in request.data:
            data['password'] = hashlib.sha1(data['password']).hexdigest()
            credentialSerializer = CredentialSerializer(credential, data=data)
        else:
            credentialSerializer = CredentialSerializerNoPassword(credential, data=data, partial=True) #??
            
        out = []
        if partySerializer.is_valid():
            partySerializer.save()
            partyReturnData = partySerializer.data
            out.append(partyReturnData)
            if credentialSerializer.is_valid():
                credentialSerializer.save()
                credentialReturnData = credentialSerializer.data
                out.append(credentialReturnData)
                return HttpResponse(json.dumps(out), content_type="application/json")
            else:
                return Response(credentialSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(partySerializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #PW-161 POST https://demoapi.arabidopsis.org/parties/institutions/
    #FORM DATA
        #username required
        #password required
        #partnerId required (tair/phoenix); (username+partnerId) must make a unique set.
        #partyType required and must be "organization"
    def post(self, request, format=None):
        if ApiKeyPermission.has_permission(request, self):
            data = request.data
            if 'partyType' not in data:
                return Response({'error': 'POST method needs partyType'}, status=status.HTTP_400_BAD_REQUEST)
            if data['partyType'] != "organization":
                return Response({'error': 'POST method. patyType must be organization'}, status=status.HTTP_400_BAD_REQUEST)
            if 'password' not in data:
                return Response({'error': 'POST method needs password'}, status=status.HTTP_400_BAD_REQUEST)
            
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
            return Response(partySerializer.errors, status=status.HTTP_400_BAD_REQUEST) 

#
    def delete(self, request, format=None):
        if not isPhoenix(request):
           return HttpResponse({'error':'does not allow delete without credentialId and secretKey query parameters'},status=status.HTTP_400_BAD_REQUEST)
        
        params = request.GET
        data = request.data
        
        if not params:
            return Response({'error':'does not allow update without query parameters'},status=status.HTTP_400_BAD_REQUEST)
        
        if 'partyId' not in request.data:
            return Response({'error':'partyId (aka institutionId) required'},status=status.HTTP_400_BAD_REQUEST)
        
        institutionId = request.data['partyId']
        
        #get party
        if Party.objects.filter(partyId = institutionId).exists():
            party = Party.objects.get(partyId = institutionId)
            party.delete()
            #credential is being deleted automatically
            return Response({'success':'delete partyId '+institutionId+'completed'},status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error':'delete '+institutionId+'failed. partyId not found in Party tbl'},status=status.HTTP_400_BAD_REQUEST)

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
        # does not allow user to update everything, too dangerous
        if not params:
            return Response({'error':'does not allow update without query parameters'})
        obj = self.get_queryset()
        out = []
        for entry in obj.PartyAffiliation.all():
            serializer = serializer_class(entry)
            out.append(serializer.data)
        return HttpResponse(json.dumps(out), content_type="application/json")
# TODO: "post" is still a security vulnerability -SC
