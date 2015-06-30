#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from metering.models import IpAddressCount, LimitValue
from django.db.models import Max
from metering.serializers import IpAddressCountSerializer, LimitValueSerializer
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

# /
class IpAddressCountCRUD(GenericCRUDView):
    queryset = IpAddressCount.objects.all()
    serializer_class = IpAddressCountSerializer

# /limits/
class LimitValueCRUD(GenericCRUDView):
    queryset = LimitValue.objects.all()
    serializer_class = LimitValueSerializer

#Increment request for an IP
# /ip/<pk>/increment/
class increment(APIView):
    def post(self, request, ip, format=None):
        partnerId = request.GET.get('partnerId')
        if IpAddressCount.objects.filter(ip=ip).exists():
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
    def get(self, request, ip, format=None):
        partnerId = request.GET.get('partnerId')
        if IpAddressCount.objects.filter(ip=ip).filter(partnerId=partnerId).exists():
            currIp = IpAddressCount.objects.get(ip=ip,partnerId=partnerId)
            if (currIp.count >= LimitValue.objects.aggregate(Max('val'))['val__max']):
                ret = {'status': "Block"}
            elif (currIp.count in LimitValue.objects.values_list('val', flat=True)):
                ret = {'status': "Warning"}
            else:
                ret = {'status': "OK"}
        else:
            # IP address not in database. not block by IP.
            ret = {'status': "OK"}
        return HttpResponse(json.dumps(ret), content_type="application/json", status=200)
