#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from metering.models import IpAddressCount, LimitValue, MeterBlacklist
from django.db.models import Max
from metering.serializers import IpAddressCountSerializer, LimitValueSerializer, MeterBlacklistSerializer
from rest_framework import generics
import json
from django.shortcuts import redirect

from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from partner.models import Partner
from common.views import GenericCRUDView

from django.db.models import F

import re
import socket
import ipaddress
import logging
logger = logging.getLogger('phoenix.api.metering')


# /
class IpAddressCountCRUD(GenericCRUDView):
    requireApiKey = False
    queryset = IpAddressCount.objects.all()
    serializer_class = IpAddressCountSerializer

# /limits/
class LimitValueCRUD(GenericCRUDView):
    queryset = LimitValue.objects.all()
    serializer_class = LimitValueSerializer

# /meterblacklist
class MeterBlacklistCRUD(GenericCRUDView):
    queryset = MeterBlacklist.objects.all()
    serializer_class = MeterBlacklistSerializer

#Increment request for an IP
# /ip/<pk>/increment/
class increment(APIView):
    def post(self, request, ip, format=None):
        partnerId = request.GET.get('partnerId')
        if IpAddressCount.objects.filter(ip=ip).filter(partnerId=partnerId).exists():
            maxCount = LimitValue.objects.aggregate(Max('val'))['val__max']
            IpAddressCount.objects.filter(count__lt=maxCount) \
                                  .filter(ip=ip) \
                                  .filter(partnerId=partnerId) \
                                  .update(count=F('count')+1)
            ret={'message':'success'}
        else:
            data = {
                "ip":ip,
                "count":1,
                "partnerId":partnerId,
            }
            serializer = IpAddressCountSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                ret={'message':'created'}
            else:
                ret={'message':'not success'}
        return HttpResponse(json.dumps(ret), content_type="application/json", status=200)

#Return limit status of IP
# /ip/<pk>/limit/
class check_limit(APIView):
    '''
    timestamp (current date and time, required)
    IP address (required)
    partner id (required)
    complete URI (required)
    status (required)
    '''
    def get(self, request, ip, format=None):
        partnerId = request.GET.get('partnerId')
        uri = request.GET.get('uri')
        """PW-287
         Change the check_limit() function to get the patterns for the specified partner by partnerId 
         and iterate through them to find any matches, 
         returning status: Block if matched and going on to the current logic if not matched.
        """

        """
        Matching Versus Searching http://www.tutorialspoint.com/python/python_reg_expressions.htm
            Python offers two different primitive operations based on regular expressions: 
            match checks for a match only at the beginning of the string, 
            while search checks for a match anywhere in the string (this is what Perl does by default).
            re.search(pattern, string, flags=0)
        """
        for meterBlackListRecord in MeterBlacklist.objects.filter(partnerId=partnerId):
            """
            re.M Makes $ match the end of a line (not just the end of the string) and 
                makes ^ match the start of any line (not just the start of the string).
            re.I Performs case-insensitive matching.   
            """
            #flags = re.M|re.I   
            searchObj = re.search(meterBlackListRecord.pattern, uri)
            if searchObj:
                ret = {'status': "BlackListBlock"}
                logger.info("Metering check_limit %s%s %s%s %s%s %s" % ("ip:",ip,"partnerId:",partnerId,"uri:",uri,ret))
                return HttpResponse(json.dumps(ret), content_type="application/json", status=200)

        if IpAddressCount.objects.filter(ip=ip).filter(partnerId=partnerId).exists():
            currIp = IpAddressCount.objects.get(ip=ip,partnerId=partnerId)
            if (currIp.count >= LimitValue.objects.filter(partnerId=partnerId).aggregate(Max('val'))['val__max']):
                ret = {'status': "Block"}
            elif (currIp.count in LimitValue.objects.filter(partnerId=partnerId).values_list('val', flat=True)):
                ret = {'status': "Warning"}
            else:
                ret = {'status': "OK"}
        else:
            # IP address not in database. not block by IP.
            ret = {'status': "OK"}
        logger.info("Metering check_limit %s%s %s%s %s%s %s" % ("ip:",ip,"partnerId:",partnerId,"uri:",uri,ret))
        return HttpResponse(json.dumps(ret), content_type="application/json", status=200)
