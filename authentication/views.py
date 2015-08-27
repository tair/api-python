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

from authentication.models import Credential, GooglePartyAffiliation
from authentication.serializers import CredentialSerializer, CredentialSerializerNoPassword
from subscription.models import Party
from partner.models import Partner
# Create your views here.

#/authentications/
class listcreateuser(GenericCRUDView):
  queryset = Credential.objects.all()

  def get_serializer_class(self):
    if self.request.method == 'GET':
      return CredentialSerializerNoPassword
    return CredentialSerializer

  def post(self, request, format=None):
        serializer_class = self.get_serializer_class()
        data = request.data
        data['password'] = hashlib.sha1(data['password']).hexdigest()
        pu = Party(); pu.save()
        data['partyId'] = pu.partyId
        serializer = serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

#/authentications/login/
def login(request):
  if request.method == 'GET':
    partyId = request.COOKIES.get('partyId')
    secretKey = request.COOKIES.get('secret_key')
    if partyId and secretKey and Credential.validate(partyId, secretKey):
      return HttpResponse(json.dumps({"bool": True}))
    return render(request,"authentication/login.html")

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
        }), status=200)
        #response.set_cookie("partyId", user.partyId.partyId, domain=".steveatgetexp.com")
        #response.set_cookie("secret_key", generateSecretKey(str(user.partyId.partyId), user.password), domain=".steveatgetexp.com")
        return response
      else:
        return HttpResponse(json.dumps({"message":"Incorrect password %s" % (requestPassword)}), status=401)
    else:
      return HttpResponse(json.dumps({"message":"No such user"}), status=401)


#/authentications/register/
def registerUser(request):
  context = {'partnerId': request.GET.get('partnerId', "")}
  return render(request, "authentication/register.html", context)

def generateSecretKey(partyId, password):
  return base64.b64encode(hmac.new(str(partyId).encode('ascii'), password.encode('ascii'), hashlib.sha1).digest())
