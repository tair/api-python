from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
import requests
import json


from authentication.models import UsernamePartyAffiliation, GooglePartyAffiliation
from subscription.models import Party
# Create your views here.

def login(request):
  if "partyId" in request.COOKIES:
    if Party.objects.filter(partyId=request.COOKIES.get('partyId')):
      response = HttpResponse("Yay!! You are logged in!")
      return response
  return render(request, "authentication/googleLogin.html")

#TODO: Accept redirect URL
def loginVerify(request):
  user = UsernamePartyAffiliation.objects.filter(username=request.POST.get('user'))
  if user:
    user = user.first()
    if ( user.password == request.POST.get('password') ):
      response = HttpResponse("Logged In")
      response.set_cookie("partyId", user.partyId_id)
      return response
  return HttpResponse("Nope")

def googleLogin(request):
  baseUrl = "https://accounts.google.com/o/oauth2/auth"
  params = { 
    'response_type': "code",
    'scope': "email openid",
    'redirect_uri': request.build_absolute_uri(reverse('authentication:googleVerify')),
    'state': request.META.get('REMOTE_ADDR'),
    'client_id': "784365841851-eir97k8btvldp33392cj3enuklm80p4n.apps.googleusercontent.com"
  }
  return redirect(urlBuilder(baseUrl, params))

def googleVerify(request):
  if request.GET.get('error'):
    return HttpResponse("You fool! You shall not pass!")
  #TODO: Add a more intelligent security string
  elif request.GET.get('state'):
    # POST code to Google to get access token
    params = {
      'code': request.GET.get('code'),
      'client_id': "784365841851-eir97k8btvldp33392cj3enuklm80p4n.apps.googleusercontent.com",
      'client_secret': "Ywh9x7VwhilM7fGVbAhFZhqb",
      'redirect_uri': request.build_absolute_uri(reverse('authentication:googleVerify')),
      'grant_type': "authorization_code"
    }
    r = requests.post("https://www.googleapis.com/oauth2/v3/token/", data=params)
    if 'error' in r.json():
      return HttpResponse(r.text)
    # Make Google API call to get email/OpenId
    s = requests.get("https://www.googleapis.com/oauth2/v1/tokeninfo", params={'id_token': r.json()['id_token']})
    if s.status_code!=200:
      return HttpResponse(s.text)
    gmailParty = GooglePartyAffiliation.objects.filter(gmail=s.json()['email'])
    response = HttpResponse()
    if gmailParty:
      response.set_cookie("partyId", gmailParty.first().partyId_id)
    return response

def urlBuilder(baseUrl, params):
  ret = baseUrl+"?"
  for key in params:
    ret += key+"="+params[key]+"&"
  return ret
