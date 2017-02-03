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

  def get_queryset(self):
    params = self.request.GET
    #get by userIdentifier
    if 'userIdentifier' in params:
        if 'partnerId' not in params:
            return 'partnerId is required.'
        userIdentifier = params['userIdentifier']
        partnerId = params['partnerId']
        queryset = Credential.objects.all().filter(userIdentifier=userIdentifier).filter(partnerId=partnerId)
        # check if credential is user credential
        obj = queryset.first()
        # if query set is empty set, return it and let the PUT function handle it
        if not obj:
            return queryset
        if obj.partyId.partyType != 'user':
            return 'cannot update credential of parties other than user type.'
    #get by username
    elif 'username' in params:
        if 'partnerId' not in params:
            return 'partnerId is required.'
        username = params['username']
        partnerId = params['partnerId']
        queryset = Credential.objects.all().filter(username=username).filter(partnerId=partnerId)
    #get by partyId
    elif 'partyId' in params:
        partyId = params['partyId']
        queryset = Credential.objects.all().filter(partyId=partyId)
    else:
        return 'invalid query parameters.'

    return queryset

  def delete(self, request):
    return Response()

  def post(self, request, format=None):
    if ApiKeyPermission.has_permission(request, self):
      serializer_class = self.get_serializer_class()
      data = request.data
      data['password'] = hashlib.sha1(data['password']).hexdigest()
      if 'partyId' in data:
        partyId = data['partyId']
        if Credential.objects.all().filter(partyId=partyId).exists():
            return Response({"non_field_errors": ["There is an existing credential for the user, use PUT to update the credential."]}, status=status.HTTP_400_BAD_REQUEST)
      if 'partyId' not in data:
        name = data['name']
        if 'display' not in data:#PW-272 
            partyData = {'name':name, 'partyType':'user','display':'0'}
        else: 
            partyData = {'name':name, 'partyType':'user','display': data['display']}
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
    queryResult = self.get_queryset()
    if type(queryResult) == str:
        return Response({'error': queryResult}, status=status.HTTP_400_BAD_REQUEST)
    obj = self.get_queryset().first()
    if not obj:
        return Response({'error': 'cannot find any record.'}, status=status.HTTP_404_NOT_FOUND)
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
        #data['password'] = generateSecretKey(str(obj.partyId.partyId), data['password'])#PW-254 and YM: TAIR-2493
        data['loginKey'] = generateSecretKey(str(obj.partyId.partyId), data['password'])
      return Response(data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#/credentials/login/
def login(request):
  if request.method == 'POST':
    ip = request.META.get('REMOTE_ADDR')
    #vet PW-223
    browser = request.META.get('HTTP_USER_AGENT')
    logging.error("Authentication Login ===")
    logging.error("Authentication Login Receiving request from %s: Client browser %s:" % (ip, browser))
    #logging.error("Client browser %s:" % browser)

    if not 'user' in request.POST:
      msg = "No username provided"
      logging.error("Authentication Login %s, %s" % (ip, msg))
      return HttpResponse(json.dumps({"message": msg}), status=400)
    if not 'password' in request.POST:
      msg = "No password provided"
      logging.error("Authentication Login %s, %s" % (ip, msg))
      return HttpResponse(json.dumps({"message": msg}), status=400)
    if not 'partnerId' in request.GET:
      msg = "No partnerId provided"
      logging.error("Authentication Login %s, %s" % (ip, msg))
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

    # iexact does not work unfortunately. Steve to find out why
    #dbUserList = Credential.objects.filter(partnerId=request.GET.get('partnerId')).filter(username__iexact=requestUser)

    # get list of users by partner and pwd -  less efficient though than fetching by (partner+username) as there could be many users with same pwd
    # more efficient is to fetch by partner+username

    dbUserList = Credential.objects.filter(partnerId=request.GET.get('partnerId')).filter(password=requestHashedPassword)

    i=0
    if not dbUserList.exists():

        msg = "PWD NOT FOUND IN DB. username existance unknown"
        logging.error("Authentication Login %s, %s: %s %s %s" % (ip, msg, requestUser, requestPassword, request.GET['partnerId']))
        return HttpResponse(json.dumps({"message":msg}), status=401)

    else:

        logging.error("Authentication Login %s USER(S) WITH PWD %s FOUND:" %(len(dbUserList), requestPassword))

        for dbUser in dbUserList:

            logging.error("Authentication Login dbUser %s requestUser %s pwd %s" % (dbUser.username,requestUser,requestPassword))

            #if user not found then continue
            if dbUser.username.lower() != requestUser.lower():
                msg = " Authentication Login USER NOT MATCH. i=%s continue..." % (i)
                logging.error(msg)
                i = i+1
                continue
            else:
                response = HttpResponse(json.dumps({
                     "message": "Correct password",
                     "credentialId": dbUser.partyId.partyId,
                     "secretKey": generateSecretKey(str(dbUser.partyId.partyId), dbUser.password),
                     "email": dbUser.email,
                     "role":"librarian",
                     "username": dbUser.username,
                     "userIdentifier": dbUser.userIdentifier,
                }), status=200)
                msg=" Authentication Login USER AND PWD MATCH. dbUser=%s requestUser=%s requestPwd=%s" % (dbUser.username, requestUser, requestPassword)
                logging.error(msg)
                return response

        logging.error("Authentication Login end of loop")
    #}end of if not empty list
    #if we did not return from above and we are here, then it's an error.
    #print last error msg from the loop and return 401 response
    logging.error("Authentication Login %s, %s: \n %s %s %s" % (ip, msg, requestUser, requestPassword, request.GET['partnerId']))
    return HttpResponse(json.dumps({"message":msg}), status=401)

def resetPwd(request):
  if request.method == 'PUT':
    if not 'user' in request.GET:
        return HttpResponse(json.dumps({"message": "No username provided"}), status=400)
    if not 'partnerId' in request.GET:
        return HttpResponse(json.dumps({"message": "No partnerId provided"}), status=400)
    requestUsername = request.GET.get('user')
    requestPartner = request.GET.get('partnerId')
    user = Credential.objects.filter(partnerId=requestPartner).filter(username__iexact=requestUsername)#PW-125 TODO
    partnerObj = Partner.objects.get(partnerId=requestPartner)
    #partnerObj = Partner.objects.get(partnerId=user.partnerId)
    if user: 
      user = user.first()
      password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
      user.password=hashlib.sha1(password).hexdigest()
      user.save()
      
      subject = "Temporary password for %s (%s)" % (user.username, user.email)#PW-215 unlikely
      '''
      message = "username: %s (%s)\n\nYour temp password is %s \n\n" \
                "Please log on to your account and change your password." \
                % (user.username, user.email, password)#PW-215
      '''          
      message = partnerObj.resetPasswordEmailBody % (user.username, user.email, password)
                
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

#/credentials/profile/
class profile(GenericCRUDView):
  queryset = Credential.objects.all()
  requireApiKey = False

  def put(self, request, format=None):
    # TODO: security risk here, get username based on the partyId verified in isPhoenix -SC
    if not isPhoenix(self.request):
      return Response(status=status.HTTP_400_BAD_REQUEST)
    # http://stackoverflow.com/questions/12611345/django-why-is-the-request-post-object-immutable
    serializer_class = CredentialSerializer
    params = request.GET
    if 'partyId' not in params:
      return Response({'error': 'Put method needs partyId'})
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
      return Response(data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# getUsernames/
class getUsernameCRUD(GenericCRUDView):
    requireApiKey = False

    def get(self, request):
        params = request.GET
        if 'email' not in params:
            return Response({'error':'email param is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not Credential.objects.all().filter(email=params['email']).filter(partnerId='phoenix').exists():
            return Response({'error':'no username found.'}, status=status.HTTP_400_BAD_REQUEST)
        usernames = Credential.objects.all().filter(email=params['email']).filter(partnerId='phoenix')
        credentialSerializer = CredentialSerializerNoPassword(usernames, many=True)

        userList = ''
        for user in credentialSerializer.data:
            userList += user['username'] + '\n'

        #send email
        subject = "Usernames for %s" % params['email']

        message = "You have the following usernames associated with %s:\n" % params['email'] + userList

        from_email = "info@phoenixbioinformatics.org"

        recipient_list = [params['email']]
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)

        return Response(credentialSerializer.data, status=status.HTTP_200_OK)