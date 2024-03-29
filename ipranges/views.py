from rest_framework import generics
from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from common.common import is_valid_ip
import ipaddress
import json

# Create your views here.
class validateip(APIView):
    def get(self, request, format=None):
        ip = request.GET.get('ip')
        try:
            if is_valid_ip(ip):
                obj = ipaddress.ip_address(ip)
                ret = {'ip version': obj.version}
                return HttpResponse(json.dumps(ret), content_type="application/json", status=200)
            else:
                ret = {'ip': "invalid"}
                return HttpResponse(json.dumps(ret), content_type="application/json", status=200)
        except ValueError:
            ret = {'ip':"error"}
            return HttpResponse(json.dumps(ret), content_type="application/json", status=200)




