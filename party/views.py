#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from party.models import Party, IpRange, Country, PartyAffiliation
from party.serializers import PartySerializer, IpRangeSerializer, CountrySerializer
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
from django.utils import timezone
from authentication.serializers import CredentialSerializer, CredentialSerializerNoPassword
from genericpath import exists
from django.db import connection
from collections import namedtuple

#below three added by Andrey for PW-277
import logging
logger = logging.getLogger('phoenix.api.party')
import traceback
#import sys

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

# /org/
class PartyOrgCRUD(GenericCRUDView):
    requireApiKey = False

    #https://demoapi.arabidopsis.org/parties/?ip=131.204.0.0  returns Auburn University
    def get(self, request, format=None):
        ip = request.GET.get('ip')
        if ip is None:
            return HttpResponse("Error. ip not provided")
        try:
            results = Party.objects.raw('SELECT p.partyId, p.name FROM Party p WHERE p.partyId in (\
            SELECT ipr.partyId FROM IpRange ipr WHERE (INET_ATON(%s) BETWEEN INET_ATON(ipr.start) AND INET_ATON(ipr.end))) \
            and (p.partyType="organization" or p.partyType="consortium")', [ip])
            out = []
            for entry in results:
                #out.append("{'partyId':'%s','partyName':'%s','subscribed':'%s'}" % (str(entry.partyId), str(entry.name), str(entry.subscribed)))
                out.append(str(entry.name)+"; ")
                logger.info("/parties/org/?ip=%s, partyId=%s, name=%s" % (ip, entry.partyId, entry.name))
            orgNames = ''.join(out)
            orgNames = orgNames[:-2]
            return HttpResponse(orgNames)
        except Exception as e:
            logger.error("Exception in /parties/org/?ip=%s, %s" % (ip, traceback.format_exc()))
            #logger.error(sys.exc_info()[0])
            return HttpResponse("")

# /orgstatus/
class PartyOrgStatusView(APIView):
    requireApiKey = False

    def get(self, request, format=None):
        if 'ip' not in request.GET:
            return Response({'error': 'ip is required'},status=status.HTTP_400_BAD_REQUEST)
        if 'partnerId' not in request.GET:
            return Response({'error': 'partnerId is required'}, status=status.HTTP_400_BAD_REQUEST)
        ip = request.GET.get('ip')
        partnerId = request.GET.get('partnerId')

        ipranges = IpRange.getByIp(ip)
        if len(ipranges) <1:
            return HttpResponse("")
        partyId = ipranges[0].partyId.partyId
        party = Party.objects.get(partyId=partyId)
        subscription = Subscription.getActiveById(partyId, partnerId)
        status = None

        if len(subscription) > 0:
            status = 'subscribed'
        else:
            status = 'not subscribed'

        ret = {
            'name': party.name,
            'status': status,
        }

        return HttpResponse(json.dumps(ret), content_type="application/json")

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
        #SELECT partyId FROM phoenix_api.Subscription where partnerId = 'tair';
        now = timezone.now()
        objs = Subscription.objects.all().filter(partnerId=partnerId).filter(startDate__lte=now).filter(endDate__gte=now).values('partyId')
        for entry in objs:
            partyList.append(entry['partyId'])

            #SELECT * from Party where partId in () and display=True and partyType='organization'
        obj = Party.objects.all().filter(partyId__in=partyList) \
                                 .filter(display=True) \
                                 .filter(partyType="organization")

        insInCons = []
        consSubList = Party.objects.all().filter(partyId__in=partyList) \
                                 .filter(partyType="consortium")
        for cons in consSubList:
            for ins in cons.PartyAffiliation.all():
                if ins.display==True and ins not in obj:
                    insInCons.append(ins)

        out = []
        for entry in obj:
            if not entry.country or not entry.country.name:#pw-265
                countryName = "not defined"
            else:
                countryName = entry.country.name
            out.append((entry.name, countryName))

        for entry in insInCons:
            if not entry.country or not entry.country.name:#pw-265
                countryName = "not defined"
            else:
                countryName = entry.country.name
            out.append((entry.name, countryName))
        return HttpResponse(json.dumps(out), content_type="application/json")

class CountryView(APIView):
    requireApiKey = False
    # def get(self, request, format=None):
    #     obj = Country.objects.all()
    #     out = []
    #     for entry in obj:
    #         out.append(entry.name)
    #     return HttpResponse(json.dumps(out), content_type="application/json")

    def get(self, request):
        countryList = Country.objects.all()
        serializer = CountrySerializer(countryList, many=True)
        return Response(serializer.data)

# /usage/
class Usage(APIView):
    requireApiKey = False
    def post(self, request, format=None):
        # security vulnerability: consortiumId should come from partyId in cookie that's been validated via isPhoenix -SC
        if not isPhoenix(request):
            return HttpResponse(status=400)
        data = request.data
        partyName = ''
        partyTypeName = ''
        if data['institution']:
            partyName = data['institution']
            partyTypeName = 'Institution'
        elif data['consortium']:
            partyName = data['consortium']
            partyTypeName = 'Consortium'
        subject = "%s Usage Request For %s" % (partyTypeName,partyName)
        message = "Partner: %s\n" \
                  "%s: %s\n" \
                  "User: %s\n" \
                  "Email: %s\n" \
                  "Start date: %s\n" \
                  "End date: %s\n" \
                  "Comments: %s\n" \
                  % (data['partner'], partyTypeName, partyName, data['name'], data['email'], data['startDate'], data['endDate'], data['comments'])
        from_email = "subscriptions@phoenixbioinformatics.org"
        recipient_list = ["subscriptions@phoenixbioinformatics.org"]
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
                return super(ConsortiumCRUD, self).get_queryset().filter(partyId=partyId).filter(partyType="consortium") #PW-161 consortium
        return []

    def get(self, request, format=None):
        if not isPhoenix(request):
           return HttpResponse({'error':'credentialId and secretKey query parameters missing or invalid'},status=status.HTTP_400_BAD_REQUEST)
        params = request.GET
        if not params['partyId']:
            return Response({'error':'does not allow get without partyId'},status=status.HTTP_400_BAD_REQUEST)

        out = []

        partyId = params['partyId']

        #get party
        if Party.objects.filter(partyId = partyId).exists():
            party = Party.objects.get(partyId = partyId)
            partySerializer = PartySerializer(party)
            out.append(partySerializer.data)
        else:
            out.append({'error':'partyId '+partyId+' not found in Party tbl'})

        #get credential
        if Credential.objects.filter(partyId = partyId).exists():
            credential = Credential.objects.get(partyId = partyId)
            credentialSerializer = CredentialSerializer(credential)
            out.append(credentialSerializer.data)
        else:
            out.append({'error':'partyId '+partyId+' not found in Credential tbl'})

        return HttpResponse(json.dumps(out), content_type="application/json")
    #PW-161 PUT https://demoapi.arabidopsis.org/parties/consortiums?credentialId=2&secretKey=7DgskfEF7jeRGn1h%2B5iDCpvIkRA%3D
    #FORM DATA partyId is required. If pwd passed it will be updated in Credential if not - not.
    # output data from both tables for a given partyId (aka consortiumId)
    def put(self, request, format=None):
        if not isPhoenix(request):
           return HttpResponse({'error':'PUT parties/consortiums/ credentialId and secretKey query parameters missing or invalid'},status=status.HTTP_400_BAD_REQUEST)

        #http://stackoverflow.com/questions/18930234/django-modifying-the-request-object
        data = request.data.copy()
        out = []

        if 'partyId' not in data:
            return Response({'error': 'PUT parties/consortiums/ partyId required'}, status=status.HTTP_400_BAD_REQUEST)

        consortiumId = data['partyId']
        #get party
        party = Party.objects.get(partyId = consortiumId)

        hasPartySerializerParam = any(param in PartySerializer.Meta.fields for param in data if param != 'partyId')
        hasCredentialSerializerParam = any(param in CredentialSerializer.Meta.fields for param in data if param != 'partyId')

        if hasCredentialSerializerParam:

            partner = Partner.objects.get(partnerId='phoenix')
            try:
                credential = Credential.objects.get(partyId=party, partnerId=partner)
            except:
                for param in ('username', 'password'):
                    if param not in data:
                        return Response({'error', 'username and password required.'}, status=status.HTTP_400_BAD_REQUEST)
                credential = Credential(partyId=party, partnerId=partner)

            if 'email' in data:
                partyIdList = Credential.objects.all().filter(email=data['email']).filter(partnerId='phoenix').values_list('partyId', flat=True)
                for partyId in partyIdList:
                    has_partyId = Party.objects.all().filter(partyId=partyId).filter(partyType='consortium').exists()
                    if has_partyId:
                        return Response({'error':'This email is already used by another consortium.'}, status=status.HTTP_400_BAD_REQUEST)

            if 'password' in data:
                if data['password'] == None or data['password'] == "":
                    return Response({'error': 'PUT parties/consortiums/ password must not be empty'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    newPwd = data['password']
                    data['password'] = Credential.generatePasswordHash(newPwd)
                    credentialSerializer = CredentialSerializer(credential, data=data, partial=True)
            else:
                credentialSerializer = CredentialSerializerNoPassword(credential, data=data, partial=True)

        partySerializer = PartySerializer(party, data=data, partial=True)

        if hasPartySerializerParam and not partySerializer.is_valid():
            return Response(partySerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if hasCredentialSerializerParam and not credentialSerializer.is_valid():
            return Response(credentialSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if hasPartySerializerParam:
            partySerializer.save()
            partyReturnData = partySerializer.data
            out.append(partyReturnData)

        if hasCredentialSerializerParam:
            credentialSerializer.save()
            credentialReturnData = credentialSerializer.data
            out.append(credentialReturnData)

        return HttpResponse(json.dumps(out), content_type="application/json")

    #PW-161 POST https://demoapi.arabidopsis.org/parties/consortiums/?credentialId=2&secretKey=7DgskfEF7jeRGn1h%2B5iDCpvIkRA%3D
    #NOTE ?/ in parties/consortiums/?credentialId=
    #FORM DATA
        #username required
        #password NOT required (latest requirement change)
        #partnerId required (tair/phoenix); (username+partnerId) must make a unique set.
        #partyType required and must be "consortium"
    def post(self, request, format=None):
        if not isPhoenix(request):
           return HttpResponse({'error':'POST parties/consortiums/ credentialId and secretKey query parameters missing or invalid'},status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()

        if 'partyType' not in data:
            return Response({'error': 'POST method needs partyType'}, status=status.HTTP_400_BAD_REQUEST)
        if data['partyType'] != "consortium":
            return Response({'error': 'POST parties/consortiums/. patyType must be consortium'}, status=status.HTTP_400_BAD_REQUEST)
        if 'email' in data:
            for partyId in Credential.objects.all().filter(email=data['email']).filter(partnerId='phoenix').values_list('partyId', flat=True):
                if Party.objects.all().filter(partyId=partyId).filter(partyType='consortium').exists():
                    return Response({'error':'This email is already used by another consortium.'}, status=status.HTTP_400_BAD_REQUEST)

        # if password is being passed and value of it is empty then error
        # not passing password in form data of POST is allowed - credential will be created with empty pwd in such case
        # boolean in pythin http://stackoverflow.com/questions/12644075/how-to-set-python-variables-to-true-or-false
        if ('password' in data):
            if (not data['password'] or data['password'] == ""):
                ### password passed and it's value is empty
                return Response({'error': 'POST parties/consortiums/ password must not be empty'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                ### password passed and it's not empty
                pwd = True
        else:
            # password is not passed
            pwd = False

        partySerializer = PartySerializer(data=data)
        if partySerializer.is_valid():
            partySerializer.save()

            out = []
            partyReturnData = partySerializer.data
            out.append(partyReturnData)

            data['partyId'] = partySerializer.data['partyId']

            if pwd == True:
                newPwd = data['password']
                data['password'] = Party.generatePasswordHash(newPwd)
                credentialSerializer = CredentialSerializer(data=data)
            else:
                credentialSerializer = CredentialSerializerNoPassword(data=data)

            if credentialSerializer.is_valid():
                credentialSerializer.save()
                credentialReturnData = credentialSerializer.data
                out.append(credentialReturnData)
                return HttpResponse(json.dumps(out), content_type="application/json", status=status.HTTP_201_CREATED)
                #return Response(credentialSerializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(credentialSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(partySerializer.errors, status=status.HTTP_400_BAD_REQUEST)

#
    def delete(self, request, format=None):
        if not isPhoenix(request):
          return HttpResponse({'error':'DELETE parties/consortiums/ credentialId and secretKey query parameters missing or invalid'},status=status.HTTP_400_BAD_REQUEST)

        params = request.GET
        # data = request.data #body in delete request is not supported by some browsers

        if not params:
            return Response({'error':'does not allow delete without query parameters'},status=status.HTTP_400_BAD_REQUEST)

        if 'partyId' not in params:
            return Response({'error':'partyId required'},status=status.HTTP_400_BAD_REQUEST)

        # consortiumId = request.data['partyId'] #body in delete request is not supported by some browsers
        consortiumId = params['partyId']

        #get party
        if Party.objects.filter(partyId = consortiumId).exists():
            party = Party.objects.get(partyId = consortiumId)
            party.delete()
            #credential is being deleted automatically
            return Response({'success':'delete partyId '+consortiumId+' completed'},status=status.HTTP_200_OK)
        else:
            return Response({'error':'delete partyId '+consortiumId+' failed. partyId not found'},status=status.HTTP_400_BAD_REQUEST)



# TODO: "post" is still a security vulnerability -SC

#PW-161 /parties/institutions/
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

    def get(self, request, format=None):
        if not isPhoenix(request):
           return HttpResponse({'error':'credentialId and secretKey query parameters missing or invalid'},status=status.HTTP_400_BAD_REQUEST)
        params = request.GET
        if not params['partyId']:
            return Response({'error':'does not allow get without partyId'},status=status.HTTP_400_BAD_REQUEST)

        out = []

        partyId = params['partyId']

        #get party
        if Party.objects.filter(partyId = partyId).exists():
            party = Party.objects.get(partyId = partyId)
            partySerializer = PartySerializer(party)
            out.append(partySerializer.data)
        else:
            out.append({'error':'partyId '+partyId+' not found in Party tbl'})

        #get credential
        if Credential.objects.filter(partyId = partyId).exists():
            credential = Credential.objects.get(partyId = partyId)
            credentialSerializer = CredentialSerializer(credential)
            out.append(credentialSerializer.data)
        else:
            out.append({'error':'partyId '+partyId+' not found in Credential tbl'})

        return HttpResponse(json.dumps(out), content_type="application/json")

    #PW-161 PUT https://demoapi.arabidopsis.org/parties/institutions?credentialId=2&secretKey=7DgskfEF7jeRGn1h%2B5iDCpvIkRA%3D
    #FORM DATA partyId is required. If pwd passed it will be updated in Credential if not - not.
    # output data from both tables for a given partyId
    def put(self, request, format=None):
        if not isPhoenix(request):
            return HttpResponse({'error':'credentialId and secretKey query parameters missing or invalid'},status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        out = []

        if 'partyId' not in data:
            return Response({'error':'partyId (aka institutionId) required'},status=status.HTTP_400_BAD_REQUEST)

        institutionId = data['partyId']
        party = Party.objects.get(partyId = institutionId)

        hasPartySerializerParam = any(param in PartySerializer.Meta.fields for param in data if param != 'partyId')
        hasCredentialSerializerParam = any(param in CredentialSerializer.Meta.fields for param in data if param != 'partyId')

        if hasCredentialSerializerParam:

            partner = Partner.objects.get(partnerId='phoenix')
            try:
                credential= Credential.objects.get(partyId=party, partnerId=partner)
            except:
                for param in ('username', 'password'):
                    if param not in data:
                        return Response({'error': 'username and password required.'}, status=status.HTTP_400_BAD_REQUEST)
                credential= Credential(partyId=party, partnerId=partner)

            if 'email' in data:
                partyIdList = Credential.objects.all().filter(email=data['email']).filter(partnerId='phoenix').values_list('partyId', flat=True)
                for partyId in partyIdList:
                    has_partyId = Party.objects.all().filter(partyId=partyId).filter(partyType='organization').exists()
                    if has_partyId:
                        return Response({'error':'This email is already used by another institution.'}, status=status.HTTP_400_BAD_REQUEST)

            if 'password' in data:
                if data['password'] == None or data['password'] == "":
                    return Response({'error': 'password must not be empty'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    newPwd = data['password']
                    data['password'] = Credential.generatePasswordHash(newPwd)
                    credentialSerializer = CredentialSerializer(credential, data=data, partial=True)
            else:
                credentialSerializer = CredentialSerializerNoPassword(credential, data=data, partial=True)

        partySerializer = PartySerializer(party, data=data, partial=True)

        if hasPartySerializerParam and not partySerializer.is_valid():
            return Response(partySerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if hasCredentialSerializerParam and not credentialSerializer.is_valid():
            return Response(credentialSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if hasPartySerializerParam:
            partySerializer.save()
            partyReturnData = partySerializer.data
            out.append(partyReturnData)

        if hasCredentialSerializerParam:
            credentialSerializer.save()
            credentialReturnData = credentialSerializer.data
            out.append(credentialReturnData)

        return HttpResponse(json.dumps(out), content_type="application/json")

    #PW-161 POST https://demoapi.arabidopsis.org/parties/institutions/?credentialId=2&secretKey=7DgskfEF7jeRGn1h%2B5iDCpvIkRA%3D
    #NOTE ?/ in parties/institutions/?credentialId=
    #FORM DATA
        #username required
        #password NOT required (latest requirement change)
        #partnerId required (tair/phoenix); (username+partnerId) must make a unique set.
        #partyType required and must be "organization"
    def post(self, request, format=None):
        if not isPhoenix(request):
           return HttpResponse({'error':'POST parties/institutions/ credentialId and secretKey query parameters missing or invalid'},status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        if 'partyType' not in data:
            return Response({'error': 'POST method needs partyType'}, status=status.HTTP_400_BAD_REQUEST)
        if data['partyType'] != "organization":
            return Response({'error': 'POST method. patyType must be organization'}, status=status.HTTP_400_BAD_REQUEST)
        if 'email' in data:
            for partyId in Credential.objects.all().filter(email=data['email']).filter(partnerId='phoenix').values_list('partyId', flat=True):
                if Party.objects.all().filter(partyId=partyId).filter(partyType='organization').exists():
                    return Response({'error':'This email is already used by another institution.'}, status=status.HTTP_400_BAD_REQUEST)

        # if password is being passed and value of it is empty then error
        # not passing password in form data of POST is allowed - credential will be created with empty pwd in such case
        # boolean in pythin http://stackoverflow.com/questions/12644075/how-to-set-python-variables-to-true-or-false
        if ('password' in data):
            if (not data['password'] or data['password'] == ""):
                ### password passed and it's value is empty
                return Response({'error': 'POST parties/institutions/ password must not be empty'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                ### password passed and it's not empty
                pwd = True
        else:
            # password is not passed
            pwd = False

        partySerializer = PartySerializer(data=data)
        if partySerializer.is_valid():
            partySerializer.save()

            out = []
            partyReturnData = partySerializer.data
            out.append(partyReturnData)

            data['partyId'] = partySerializer.data['partyId']

            if pwd == True:
                newPwd = data['password']
                data['password'] = Party.generatePasswordHash(newPwd)
                credentialSerializer = CredentialSerializer(data=data)
            else:
                credentialSerializer = CredentialSerializerNoPassword(data=data)

            if credentialSerializer.is_valid():
                credentialSerializer.save()
                credentialReturnData = credentialSerializer.data
                out.append(credentialReturnData)
                return HttpResponse(json.dumps(out), content_type="application/json", status=status.HTTP_201_CREATED)
                #return Response(credentialSerializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(credentialSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(partySerializer.errors, status=status.HTTP_400_BAD_REQUEST)

#
    def delete(self, request, format=None):
        if not isPhoenix(request):
           return HttpResponse({'error':'credentialId and secretKey query parameters missing or invalid'},status=status.HTTP_400_BAD_REQUEST)

        params = request.GET
        # data = request.data #body in delete request is not supported by some browsers

        if not params:
            return Response({'error':'does not allow update without query parameters'},status=status.HTTP_400_BAD_REQUEST)

        if 'partyId' not in params:
            return Response({'error':'partyId (aka institutionId) required'},status=status.HTTP_400_BAD_REQUEST)

        # institutionId = request.data['partyId'] #body in delete request is not supported by some browsers
        institutionId = params['partyId']

        #get party
        if Party.objects.filter(partyId = institutionId).exists():
            party = Party.objects.get(partyId = institutionId)
            party.delete()
            #credential is being deleted automatically
            return Response({'success':'delete partyId '+institutionId+' completed'},status=status.HTTP_200_OK)
        else:
            return Response({'error':'delete partyId '+institutionId+' failed. partyId not found'},status=status.HTTP_400_BAD_REQUEST)

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
       if obj:
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
           return Response({'error':'does not allow creation without parentPartyId or childPartyId'},status=status.HTTP_400_BAD_REQUEST)
       parentPartyId = params['parentPartyId']
       childPartyId = params['childPartyId']
       if Party.objects.all().get(partyId = parentPartyId):
           parentParty = Party.objects.all().get(partyId=parentPartyId)
       else:
           return Response({'error':'parentParty does not exist'},status=status.HTTP_400_BAD_REQUEST)
       if Party.objects.all().get(partyId = childPartyId):
           childParty=Party.objects.all().get(partyId=childPartyId)
       else:
           return Response({'error':'childParty does not exist'},status=status.HTTP_400_BAD_REQUEST)
       PartyAffiliation.objects.create(childPartyId=childParty,parentPartyId=parentParty)
       serializer = serializer_class(childParty)
       return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, format=None):
       if not isPhoenix(self.request):
           return HttpResponse(status=400)
       serializer_class = self.get_serializer_class()
       params = request.GET
       if not params['parentPartyId'] or not params['childPartyId']:
           return Response({'error':'does not allow deletion without query parameters'})
       parentPartyId = params['parentPartyId']
       childPartyId = params['childPartyId']
       if Party.objects.all().get(partyId=parentPartyId):
           parentParty = Party.objects.all().get(partyId=parentPartyId)
       else:
           return Response({'error':'cannot find parent party'}, status=status.HTTP_400_BAD_REQUEST)
       if Party.objects.all().get(partyId=childPartyId):
           childParty=Party.objects.all().get(partyId=childPartyId)
       else:
           return Response({'error':'cannot find child party'}, status=status.HTTP_400_BAD_REQUEST)
       PartyAffiliation.objects.filter(childPartyId=childParty, parentPartyId=parentParty).delete()
       serializer = serializer_class(childParty)
       return Response(serializer.data)

    def put(self, request, format=None):
        return Response({'error':'put function is unavailable'}, status=status.HTTP_400_BAD_REQUEST)
# TODO: "post" is still a security vulnerability -SC
