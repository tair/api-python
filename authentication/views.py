from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.core.mail import send_mail

import requests
import json
import base64, hmac, hashlib
import string
import random
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from common.views import GenericCRUDView
from common.permissions import ApiKeyPermission 

from authentication.models import Credential, GooglePartyAffiliation
from authentication.serializers import CredentialSerializer, CredentialSerializerNoPassword
from subscription.models import Party
from partner.models import Partner
from party.serializers import PartySerializer
from party.models import Party

from common.permissions import isPhoenix

import logging

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
        name = data['name']
        partyData = {'name':name, 'partyType':'user'}
        partySerializer = PartySerializer(data=partyData, partial =True)
        # pu = Party(); pu.save()
        # data['partyId'] = pu.partyId
        if partySerializer.is_valid():
          partySerializer.save()
          data['partyId'] = partySerializer.data['partyId']
      serializer = serializer_class(data=data)
      if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
  
  def put(self, request, format=None):
    # TODO: security risk here, get username based on the partyId verified in isPhoenix -SC
    if not isPhoenix(self.request):
      return Response(status=status.HTTP_400_BAD_REQUEST)
    # http://stackoverflow.com/questions/12611345/django-why-is-the-request-post-object-immutable
    serializer_class = self.get_serializer_class()
    params = request.GET
    if 'userIdentifier' not in params:
      return Response({'error': 'Put method needs userIdentifier'})
    obj = self.get_queryset().first()
    #http://stackoverflow.com/questions/18930234/django-modifying-the-request-object PW-123
    data = request.data.copy() # PW-123
    if 'password' in data:
      data['password'] = hashlib.sha1(data['password']).hexdigest()
    serializer = serializer_class(obj, data=data, partial=True)
    if serializer.is_valid():
      serializer.save()
      #update party info
      if 'partyId' in serializer.data:
        partyId = serializer.data['partyId']
        partyObj = Party.objects.all().get(partyId = partyId)
        if 'name' in data:
          name = data['name']
          partyData = {'name':name}
        partySerializer = PartySerializer(partyObj, data=partyData, partial =True)
        if partySerializer.is_valid():
          partySerializer.save()
      if 'password' in data:
        # HACK: 2015-11-12: YM: TAIR-2493: The new secret key (a.k.a. login key) is being returned as 'password' attribute. Should be refactored to use 'loginKey' attribute.
        data['password'] = generateSecretKey(str(obj.partyId.partyId), data['password'])
      return Response(data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#/credentials/login/
def login(request):
  if request.method == 'POST':
    import os
    dirname = os.path.dirname(os.path.realpath(__file__))
    logging.basicConfig(filename="%s/logs/login.log" % dirname,
                        format='%(asctime)s %(message)s'
    )

    ip = request.META.get('REMOTE_ADDR')
    #vet PW-223
    browser = request.META['HTTP_USER_AGENT']
    logging.error("-------------------------")
    logging.error("Receiving request from %s: Client browser %s:" % (ip, browser))
    #logging.error("Client browser %s:" % browser)

    if not 'user' in request.POST:
      msg = "No username provided"
      logging.error("%s, %s" % (ip, msg))
      return HttpResponse(json.dumps({"message": msg}), status=400)
    if not 'password' in request.POST:
      msg = "No password provided"
      logging.error("%s, %s" % (ip, msg))
      return HttpResponse(json.dumps({"message": msg}), status=400)
    if not 'partnerId' in request.GET:
      msg = "No partnerId provided"
      logging.error("%s, %s" % (ip, msg))
      return HttpResponse(json.dumps({"message": msg}), status=400)
 
    #   msg = "Incorrect password"
    #   logging.error("%s, %s: %s %s %s" % (ip, msg, request.POST['user'], request.POST['password'], request.GET['partnerId']))
    #   return HttpResponse(json.dumps({"message":msg}), status=401)
    
    #  msg = "No such user"
    #  logging.error("%s, %s: %s %s %s" % (ip, msg, request.POST['user'], request.POST['password'], request.GET['partnerId']))
    #  return HttpResponse(json.dumps({"message":msg}), status=401)
  
    requestPassword = request.POST.get('password')
    requestHashedPassword = hashlib.sha1(request.POST.get('password')).hexdigest()
    requestUser = request.POST.get('user')
    # get list of users by partner and pwd
    #logging.error("---")
    dbUserList = Credential.objects.filter(partnerId=request.GET.get('partnerId')).filter(password=requestHashedPassword)
    i=0
    if not dbUserList.exists():
        msg = "userList empty. PWD NOT FOUND in db"
        logging.error("%s, %s: %s %s %s" % (ip, msg, requestUser, requestPassword, request.GET['partnerId']))
        return HttpResponse(json.dumps({"message":msg}), status=401)
    else:
        logging.error("found %s user(s) with this PWD %s starting loop" %(len(dbUserList), requestPassword))
        for dbUser in dbUserList:
            #if USER FOUND by lower-cased name comparison then check his pwd
            if dbUser.username.lower() == requestUser.lower(): 
                #if pwd match return success else continue to iterate
                if dbUser.password == requestHashedPassword:
                    msg="USER FOUND by lower-cased name comparison. PWD MATCH. dbUser=%s requestUser=%s requestPwd=%s" % (dbUser.username, requestUser, requestPassword)
                    response = HttpResponse(json.dumps({
                     "message": "Correct password", 
                     "credentialId": dbUser.partyId.partyId,
                     "secretKey": generateSecretKey(str(dbUser.partyId.partyId), dbUser.password),
                     "email": dbUser.email,
                     "role":"librarian",
                     "username": dbUser.username,
                    }), status=200)
                    logging.error("Successful login from %s: %s" % (ip, request.POST['user']))
                    return response
                #USER FOUND but PWD NOT MATCH. check next user in the loop
                else:
                    msg="USER FOUND (dBuser=%s requestUser=%s) by lower-cased name comparison and PWD NOT MATCH (pwd=%s) iteration i=%s continue ..."  % (dbUser.username, requestUser, requestPassword, i)
                    logging.error(msg)
                    i = i+1
                    continue
            #if USER NOT FOUND then log error and check next user in the loop
            else:
                msg = "USER NOT FOUND so far by lower-cased name comparison. iteration i=%s dbUser=%s requestUser=%s pwd= %s continue..." % (i, dbUser.username, requestUser, requestPassword)
                logging.error(msg)
                i = i+1 
                continue
        logging.error("end of loop")
    #}end of if not empty list
    #if we did not return with success from above and we are here, then it's an error. 
    #print last error msg from the loop and return 401 response
    logging.error("%s, %s: \n %s %s %s" % (ip, msg, requestUser, requestPassword, request.GET['partnerId']))
    return HttpResponse(json.dumps({"message":msg}), status=401)
    

def resetPwd(request):
  if request.method == 'PUT':
    if not 'user' in request.GET:
        return HttpResponse(json.dumps({"message": "No username provided"}), status=400)
    if not 'partnerId' in request.GET:
        return HttpResponse(json.dumps({"message": "No partnerId provided"}), status=400)
    requestUsername = request.GET.get('user')
    requestPartner = request.GET.get('partnerId')
    user = Credential.objects.filter(partnerId=requestPartner).filter(username__iexact=requestUsername)#PW-125
    
    if user: 
      user = user.first()
      password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
      user.password=hashlib.sha1(password).hexdigest()
      user.save()
      
      subject = "Temporary password for %s (%s)" % (user.username, user.email)#PW-215 unlikely
      message = "username: %s (%s)\n\nYour temp password is %s \n\n" \
                "Please log on to your account and change your password." \
                % (user.username, user.email, password)#PW-215
      from_email = "info@phoenixbioinformatics.org"
      recipient_list = [user.email]
      send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
            
      return HttpResponse(json.dumps({'reset pwd':'success', 'username':user.username, 'useremail':user.email, 'temppwd':user.password}), content_type="application/json")#PW-215 unlikely
    return HttpResponse(json.dumps({"reset pwd failed":"No such user"}), status=401)
#/credentials/register/
#https://demoapi.arabidopsis.org/credentials/register
def registerUser(request):
  context = {'partnerId': request.GET.get('partnerId', "")}
  return render(request, "authentication/register.html", context)

def generateSecretKey(partyId, password):
  return base64.b64encode(hmac.new(str(partyId).encode('ascii'), password.encode('ascii'), hashlib.sha1).digest())
