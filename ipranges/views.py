from rest_framework import generics
from django.http import Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
import socket
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


def is_valid_ipv4(ip_str):
    """
    Check the validity of an IPv4 address
    """
    try:
        socket.inet_pton(socket.AF_INET, ip_str)
    except AttributeError:
        try:
            socket.inet_aton(ip_str)
        except socket.error:
            return False
        return ip_str.count('.') == 3
    except socket.error:
        return False
    return True


def is_valid_ipv6(ip_str):
    """
    Check the validity of an IPv6 address
    """
    try:
        socket.inet_pton(socket.AF_INET6, ip_str)
    except socket.error:
        return False
    return True


def is_valid_ip(ip_str):
    """
    Check the validity of an IP address
    """
    return is_valid_ipv4(ip_str) or is_valid_ipv6(ip_str)


