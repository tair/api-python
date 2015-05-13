#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from metering.models import ipAddr, limits
from django.db.models import Max
from metering.serializers import ipSerializer, limitSerializer
from rest_framework import generics
import json

from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from partner.models import Partner
###############################################For IP##############################################
#List view of all IP counts
class ipList(APIView):
    def get(self, request, format=None):
        ips = Partner.filters(self, ipAddr.objects.all(), "partner")
        serializer = ipSerializer(ips, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def post(self, request, format=None):
        if request.GET.get('partnerId', 'None') is None:
          return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.GET.get('partnerId')!=request.data['partner']:
          raise Http404
        checkIp = Partner.filters(self, ipAddr.objects.all(), "partner").filter(ip=request.data['ip'])
        if checkIp:
          return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = ipSerializer(data=request.data)
        if serializer.is_valid():
          serializer.save()
          return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        ips = Partner.filters(self, ipAddr.objects.all(), "partner")
        if ips:
          ips.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


#Detail view for each IP
class ipDetail(APIView):
    def get(self, request, pk, format=None):
        snippet = Partner.filters(self, ipAddr.objects.all(), "partner")
        if snippet:
          snippet = snippet.get(ip=pk)
          serializer = ipSerializer(snippet)
        else:
          serializer = ipSerializer(snippet, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, format=None):
        snippet = Partner.filters(self, ipAddr.objects.all(), "partner")
        if snippet:
          snippet = snippet.get(ip=pk)
          snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, pk, format=None):
        snippet = Partner.filters(self, ipAddr.objects.all(), "partner")
        if snippet:
          snippet.get(ip=pk)
        serializer = ipSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
        
#Increment request for an IP
class increment(APIView):
  def get(self, request, ip, format=None):
    currIp = Partner.filters(self, ipAddr.objects.all(), "partner")
    if currIp:
      currIp = currIp.get(ip=ip)
    #TODO: if (currIp.count < get_limit("MeteringLimit")):
      currIp.count += 1
      currIp.save()
    #TODO:
    return redirect('/meters/ip/'+ip+'/')

############################################For Limits#############################################
#Return limit status of IP
class check_limit(APIView):
  def get(self, request, ip, format=None):
    currIp = Partner.filters(self, ipAddr.objects.all(), "partner")
    limitVal = Partner.filters(self, limits.objects.all(), "partner")
    if currIp:
      currIp = currIp.get(ip=ip)
    if not limitVal:
      return Response(status=status.HTTP_400_BAD_REQUEST)
    
    if (currIp.count >= limitVal.aggregate(Max('val'))['val__max']):
        ret = {'status': "Block"}
    elif (currIp.count in limitVal.values_list('val', flat=True)):
        ret = {'status': "Warning"}
    else:
        ret = {'status': "OK"}
    return HttpResponse(json.dumps(ret), content_type="application/json", status=200)

#Detail view/update for warning limit
class warningLimit(APIView):
    def get(self, request, format=None):
        limit = Partner.filters(self, limits.objects.all(), "partner")
        serializer = limitSerializer(limit, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        if request.GET.get('partnerId', 'None') is None:
          return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.GET.get('partnerId')!=request.data['partner']:
          raise Http404
        checkLimit = Partner.filters(self, limits.objects.all(), "partner").filter(val=request.data['val'])
        if checkILimit:
          return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = limitSerializer(data=request.data)
        if serializer.is_valid():
          serializer.save()
          return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

#Detail view/update for metering limit
class meteringLimit(APIView):
    def get(self, request, format=None):
        limit = Partner.filters(self, limits.objects.all(), "partner")
        if limit:
          limit = limit.order_by('val').last()
          serializer = limitSerializer(limit)
        else:
          serializer = limitSerializer(limit, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, format=None):
        snippet = Partner.filters(self, limits.objects.all(), "partner")
        if snippet:
          snippet = snippet.order_by('val').last()
        serializer = ipSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
###########################################Auxillary functions#####################################
