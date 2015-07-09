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

from authentication.models import User, GooglePartyAffiliation
from authentication.serializers import UserSerializer, UserSerializerNoPassword
from subscription.models import Party
from partner.models import Partner
# Create your views here.

#/authentications/
class listcreateuser(GenericCRUDView):
  queryset = User.objects.all()

  def get_serializer_class(self):
    if self.request.method == 'GET':
      return UserSerializerNoPassword
    return UserSerializer

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
    if partyId and secretKey and User.validate(partyId, secretKey):
      return HttpResponse(json.dumps({"bool": True}))
    return render(request,"authentication/login.html")

  if request.method == 'POST':
    requestUsername = request.POST.get('user')
    requestPassword = hashlib.sha1(request.POST.get('password')).hexdigest()
    user = User.objects.filter(username=requestUsername)
    
    if user: 
      user = user.first()
      if ( user.password == requestPassword ):
        response = HttpResponse(json.dumps({"message": "Correct password"}))
        response.set_cookie("partyId", user.partyId.partyId)
        response.set_cookie("secret_key", generateSecretKey(str(user.partyId.partyId), user.password))
        return response
      else:
        return HttpResponse(json.dumps({"message":"Incorrect password %s" % (requestPassword)}))
    else:
      return HttpResponse(json.dumps({"message":"No user"}))


#/authentications/register/
def registerUser(request):
  context = {'partnerId': request.GET.get('partnerId', "")}
  return render(request, "authentication/register.html", context)

def generateSecretKey(partyId, password):
  return base64.b64encode(hmac.new(str(partyId).encode('ascii'), password.encode('ascii'), hashlib.sha1).digest())

#class adduser(APIView):
#  def post(self, request, format=None):
#    partnerId = request.GET.get('partnerId', None)
#    if (partnerId is not None) and (Partner.objects.filter(partnerId=partnerId)):
#      pu = Party(partyType="user")
#      pu.save()
#      UsernamePartyAffiliation(username=request.data['username'], 
#                         password=request.data['password'], 
#                         email=request.data['email'], 
#                         organization=request.data['organization'],
#                         partyId=pu).save()
#      return HttpResponse("User created", 200)
#    return HttpResponse("Access denied", 403)

#def googleLogin(request):
#  baseUrl = "https://accounts.google.com/o/oauth2/auth"
#  params = { 
#    'response_type': "code",
#    'scope': "email openid",
#    'redirect_uri': request.build_absolute_uri(reverse('authentication:googleVerify')),
#    'state': request.META.get('REMOTE_ADDR'),
#    'client_id': "784365841851-eir97k8btvldp33392cj3enuklm80p4n.apps.googleusercontent.com"
#  }
#  return redirect(urlBuilder(baseUrl, params))
#
#def googleVerify(request):
#  if request.GET.get('error'):
#    return HttpResponse("You fool! You shall not pass!")
#  #TODO: Add a more intelligent security string
#  elif request.GET.get('state'):
#    # POST code to Google to get access token
#    params = {
#      'code': request.GET.get('code'),
#      'client_id': "784365841851-eir97k8btvldp33392cj3enuklm80p4n.apps.googleusercontent.com",
#      'client_secret': "Ywh9x7VwhilM7fGVbAhFZhqb",
#      'redirect_uri': request.build_absolute_uri(reverse('authentication:googleVerify')),
#      'grant_type': "authorization_code"
#    }
#    r = requests.post("https://www.googleapis.com/oauth2/v3/token/", data=params)
#    if 'error' in r.json():
#      return HttpResponse(r.text)
#    # Make Google API call to get email/OpenId
#    s = requests.get("https://www.googleapis.com/oauth2/v1/tokeninfo", params={'id_token': r.json()['id_token']})
#    if s.status_code!=200:
#      return HttpResponse(s.text)
#    gmailParty = GooglePartyAffiliation.objects.filter(gmail=s.json()['email'])
#    response = HttpResponse()
#    if gmailParty:
#      response.set_cookie("partyId", gmailParty.first().partyId_id)
#    return response
#
#def urlBuilder(baseUrl, params):
#  ret = baseUrl+"?"
#  for key in params:
#    ret += key+"="+params[key]+"&"
#  return ret
