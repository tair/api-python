from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
import requests
import json
import base64, hmac, hashlib
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from common.views import GenericCRUDView
from common.permissions import ApiKeyPermission

from authentication.models import Credential, GooglePartyAffiliation
from authentication.serializers import CredentialSerializer, CredentialSerializerNoPassword
from subscription.models import Party

def get_serializer_class(self):
    return CredentialSerializer

serializer_class = get_serializer_class()
params = {'username':'tair2468','password':'234','email':'tair2468_1@test.cn','institution':'QL ins','partnerId':'tair','userIdentifier':'1501492704'}
if 'username' not in params:
    print 'error: Put method needs username'
generic_crud = GenericCRUDView(generics.GenericAPIView)
obj = generic_crud.get_queryset().first()
data = {'username':'tair2468','password':'234','email':'tair2468_1@test.cn','institution':'QL ins','partnerId':'tair','userIdentifier':'1501492704'}
if 'password' in data:
    data['password'] = hashlib.sha1(data['password']).hexdigest()
serializer = serializer_class(obj, data=data, partial=True)
if serializer.is_valid():
    serializer.save()
    print "update successful: "+data
else:
    print "serializer invalid"