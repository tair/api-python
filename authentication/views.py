from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.core.mail import send_mail

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
from partner.models import Partner

from common.permissions import isPhoenix

# Create your views here.

#/credentials/
class listcreateuser(GenericCRUDView):
  queryset = Credential.objects.all()
  requireApiKey = False

  def get_serializer_class(self):
    if self.request.method == 'GET':
      return CredentialSerializerNoPassword
    return CredentialSerializer

  def delete(self, request):
    return Response()

  def post(self, request, format=None):
    if ApiKeyPermission.has_permission(request, self):
      serializer_class = self.get_serializer_class()
      data = request.data
      data['password'] = hashlib.sha1(data['password']).hexdigest()
      if 'partyId' not in data:
        pu = Party(); pu.save()
        data['partyId'] = pu.partyId
      serializer = serializer_class(data=data)
      if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

  def put(self, request, format=None):
    # TODO: security risk here, get username based on the partyId verified in isPhoenix -SC
    # if not isPhoenix(self.request):
    #   return Response(status=status.HTTP_400_BAD_REQUEST)

    serializer_class = self.get_serializer_class()
    params = request.GET
    if 'username' not in params:
      return Response({'error': 'Put method needs username'})
    # obj = self.get_queryset().first()
    obj = Credential.objects.all().get(userIdentifier='1501492704')
    data = request.data
    if 'password' in data:
      data['password'] = hashlib.sha1(data['password']).hexdigest()
    serializer = serializer_class(obj, data=data, partial=True)
    if serializer.is_valid():
      serializer.save()
      # return Response(serializer.data, status=status.HTTP_201_CREATED)
      return Response("update successfull")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#/credentials/login/
def login(request):
  if request.method == 'POST':
    if not 'user' in request.POST:
        return HttpResponse(json.dumps({"message": "No username provided"}), status=400)
    if not 'password' in request.POST:
        return HttpResponse(json.dumps({"message": "No password provided"}), status=400)
    if not 'partnerId' in request.GET:
        return HttpResponse(json.dumps({"message": "No partnerId provided"}), status=400)
    requestUsername = request.POST.get('user')
    requestPassword = hashlib.sha1(request.POST.get('password')).hexdigest()
    requestPartner = request.GET.get('partnerId')
    user = Credential.objects.filter(partnerId=requestPartner).filter(username=requestUsername)
    
    if user: 
      user = user.first()
      if ( user.password == requestPassword ):
        response = HttpResponse(json.dumps({
          "message": "Correct password", 
          "partyId": user.partyId.partyId, 
          "secret_key": generateSecretKey(str(user.partyId.partyId), user.password),
          "email": user.email,
          "role":"librarian",
	  "username": user.username,
        }), status=200)
        return response
      else:
        return HttpResponse(json.dumps({"message":"Incorrect password %s" % (requestPassword)}), status=401)
    else:
      return HttpResponse(json.dumps({"message":"No such user"}), status=401)
# PW-123
#/credentials/forgot/
#user,partnerId
def ForgotPassword(request):
  if request.method == 'POST':
    if not 'user' in request.POST:
        return HttpResponse(json.dumps({"message": "No username provided"}), status=400)
    requestUsername = request.POST.get('user')
    requestPartner = request.GET.get('partnerId')
    user = Credential.objects.filter(partnerId=requestPartner).filter(username=requestUsername)
    # https://demoapi.arabidopsis.org/credentials/register
    if user: 
        user = user.first()
        subject = "%s Reset Password For %s" % (user.username, user.email)
        message = "%s (%s)\n" \
                  "\n" \
                  "Your temp password is XXX \n" \
                  % (user.username, user.email)
        from_email = "info@phoenixbioinformatics.org"
        recipient_list = [user.email, "info@phoenixbioinformatics.org"]
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
        return HttpResponse(json.dumps({'message':'success', 'username':user.username, 'useremail':user.email}), content_type="application/json")
    else:
      return HttpResponse(json.dumps({"message":"No such user"}), status=401)

#/credentials/register/
#https://demoapi.arabidopsis.org/credentials/register
def registerUser(request):
  context = {'partnerId': request.GET.get('partnerId', "")}
  return render(request, "authentication/register.html", context)

def generateSecretKey(partyId, password):
  return base64.b64encode(hmac.new(str(partyId).encode('ascii'), password.encode('ascii'), hashlib.sha1).digest())
