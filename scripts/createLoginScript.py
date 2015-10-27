import django
import os
import csv

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

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

serializer_class = CredentialSerializer
params = {'username':'tair2468','password':'234','email':'tair2468_1@test.cn','institution':'QL ins','partnerId':'tair','userIdentifier':'1501492704'}
if 'username' not in params:
    print 'error: Put method needs username'
obj = Credential.objects.all().get(userIdentifier='1501492704')
data = {'username':'tair2468','password':'234','email':'tair2468_1@test.cn','institution':'QL ins','partnerId':'tair','userIdentifier':'1501492704'}
if 'password' in data:
    data['password'] = hashlib.sha1(data['password']).hexdigest()
serializer = serializer_class(obj, data=data, partial=True)
if serializer.is_valid():
    serializer.save()
    print "update successful: "+data
else:
    print "serializer invalid"