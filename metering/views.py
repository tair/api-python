#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.




from metering.models import ipAddr, limits
from metering.serializers import ipSerializer, limitSerializer
from rest_framework import generics
import json

from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect

###############################################For IP##############################################
#List view of all IP counts
class ipList(APIView):
    def get(self, request, format=None):
        ips = ipAddr.objects.using('mySQLTest').all()
        serializer = ipSerializer(ips, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def post(self, request, format=None):
        ip = request.data['ip']
        try:
            ipAddr.objects.get(ip=ip)
            return Response(status=HTTP_400_BAD_REQUEST)
        except:
            u = ipAddr(ip=ip, count=1)
            u.save(using='mySQLTest')
            serializer = ipSerializer(u)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, format=None):
        ipAddr.objects.using('mySQLTest').all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

#Detail view for each IP
class ipDetail(APIView):
    def get(self, request, pk, format=None):
        snippet = get_object(pk)
        serializer = ipSerializer(snippet)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, format=None):
        snippet = get_object(pk)
        snippet.delete(using='mySQLTest')
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, pk, format=None):
        snippet = get_object(pk)
        serializer = ipSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
        
#Increment request for an IP
def increment(request, ip, format=None):
    currIp = get_object(ip)
    if (currIp.count < get_limit("MeteringLimit")):
        currIp.count += 1
        currIp.save(using='mySQLTest')
    return redirect('/meters/ip/'+ip)

############################################For Limits#############################################
#Return limit status of IP
def check_limit(request, ip, format=None):
    currIp = get_object(ip)
    if (currIp.count == get_limit("WarningLimit").val):
        ret = {'status': "Warning"}
    elif (currIp.count < get_limit("MeteringLimit").val):
        ret = {'status': "OK"}
    else:
        ret = {'status': "Block"}
    return HttpResponse(json.dumps(ret), content_type="application/json", status=200)

#Detail view/update for warning limit
class warningLimit(APIView):
    def get(self, request, format=None):
        limit = get_limit("WarningLimit")
        serializer = limitSerializer(limit)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, format=None):
        limit = get_create_limit("WarningLimit")
        limit.val = request.data['limit']
        limit.save(using='mySQLTest')
        serializer = limitSerializer(limit)
        return Response(serializer.data, status=status.HTTP_200_OK)

#Detail view/update for metering limit
class meteringLimit(APIView):
    def get(self, request, format=None):
        limit = get_limit("MeteringLimit")
        serializer = limitSerializer(limit)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, format=None):
        limit = get_create_limit("MeteringLimit")
        limit.val = request.data['limit']
        limit.save(using='mySQLTest')
        serializer = limitSerializer(limit)
        return Response(serializer.data, status=status.HTTP_200_OK)


###########################################Auxillary functions#####################################
def get_object(pk):
    try:
        return ipAddr.objects.using('mySQLTest').get(ip=pk)
    except ipAddr.DoesNotExist:
        #TODO: Put status message for debug
        raise Http404

def get_limit(lm):
    try: 
        return limits.objects.using('mySQLTest').get(name=lm)
    except:
        #TODO: Put status message for debug
        raise Http404

def get_create_limit(lm):
    try:
        return limits.objects.get(name=lm)
    except:
        u = limits(name=lm, val=0)
        u.save()
        return u
        
##Check if IP exceeds warning limit
#def exceedsWarningLimit(request, ip):
#    currIp = get_object(ip)
#    ret = {
#        'bool': (currIp.count > limits.objects.get(name="WarningLimit").val)
#    }
#    return HttpResponse(json.dumps(ret), content_type="application/json", status=200)
#
##Check if IP exceeds metering limit
#def exceedsMeteringLimit(request, ip):
#    currIp = get_object(ip)
#    ret = {
#        'bool': (currIp.count > limits.objects.get(name="MeteringLimit").val)
#    }
#    return HttpResponse(json.dumps(ret), content_type="application/json", status=200)
