from django.shortcuts import render, redirect
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
logger = logging.getLogger('phoenix.api.authentication')

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
        #comment out for biocyc compatibility
        if 'partnerId' not in params:
           return 'partnerId is required.'
        userIdentifier = params['userIdentifier']
        partnerId = params['partnerId']
        queryset = Credential.objects.all().filter(userIdentifier=userIdentifier).filter(partnerId=partnerId)
        if len(queryset) > 1:
            return "Found more than one record with the same user identifier. Please contact dev@phoenixbioinformatics.org for assistant."
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
      data = request.data.copy() # PW-660
      data['password'] = Credential.generatePasswordHash(data['password'])
      if 'partyId' in data:
        partyId = data['partyId']
        if Credential.objects.all().filter(partyId=partyId).exists():
            return Response({"non_field_errors": ["There is an existing credential for the user, use PUT to update the credential."]}, status=status.HTTP_400_BAD_REQUEST)
      if 'userIdentifier' in data:
        userIdentifier = data['userIdentifier']
        if userIdentifier is not None:
          partnerId = data['partnerId']
          if Credential.objects.all().filter(userIdentifier=userIdentifier).filter(partnerId=partnerId).exists():
            return Response({"non_field_errors": ["User identifier already exists, use PUT to update the credential or provide an unique user identifier."]}, status=status.HTTP_400_BAD_REQUEST)
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
      data['password'] = Credential.generatePasswordHash(data['password'])
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
        #data['password'] = Credential.generateSecretKey(str(obj.partyId.partyId), data['password'])#PW-254 and YM: TAIR-2493
        data['loginKey'] = Credential.generateSecretKey(str(obj.partyId.partyId), data['password'])
      return Response(data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#/credentials/login/
def login(request):
  if request.method == 'POST':
    ip = request.META.get('REMOTE_ADDR')
    #vet PW-223
    browser = request.META.get('HTTP_USER_AGENT')
    logger.info("Authentication Login ===")
    logger.info("Authentication Login Receiving request from %s: Client browser %s:" % (ip, browser))
    #logger.info("Client browser %s:" % browser)

    if not 'user' in request.POST:
      msg = "No username provided"
      logger.info("Authentication Login %s, %s" % (ip, msg))
      return HttpResponse(json.dumps({"message": msg}), status=400)
    if not 'password' in request.POST:
      msg = "No password provided"
      logger.info("Authentication Login %s, %s" % (ip, msg))
      return HttpResponse(json.dumps({"message": msg}), status=400)
    if not 'partnerId' in request.GET:
      msg = "No partnerId provided"
      logger.info("Authentication Login %s, %s" % (ip, msg))
      return HttpResponse(json.dumps({"message": msg}), status=400)

    #   msg = "Incorrect password"
    #   logger.info("%s, %s: %s %s %s" % (ip, msg, request.POST['user'], request.POST['password'], request.GET['partnerId']))
    #   return HttpResponse(json.dumps({"message":msg}), status=401)

    #  msg = "No such user"
    #  logger.info("%s, %s: %s %s %s" % (ip, msg, request.POST['user'], request.POST['password'], request.GET['partnerId']))
    #  return HttpResponse(json.dumps({"message":msg}), status=401)

    requestPassword = request.POST.get('password')
    requestHashedPassword = Credential.generatePasswordHash(request.POST.get('password'))
    requestUser = request.POST.get('user')

    # iexact does not work unfortunately. Steve to find out why
    #dbUserList = Credential.objects.filter(partnerId=request.GET.get('partnerId')).filter(username__iexact=requestUser)

    # get list of users by partner and pwd -  less efficient though than fetching by (partner+username) as there could be many users with same pwd
    # more efficient is to fetch by partner+username

    dbUserList = Credential.objects.filter(partnerId=request.GET.get('partnerId')).filter(password=requestHashedPassword)

    i=0
    if not dbUserList.exists():

        msg = "PWD NOT FOUND IN DB. username existance unknown"
        logger.info("Authentication Login %s, %s: %s %s %s" % (ip, msg, requestUser, requestHashedPassword, request.GET['partnerId']))
        return HttpResponse(json.dumps({"message":msg}), status=401)

    else:

        logger.info("Authentication Login %s USER(S) WITH PWD %s FOUND:" %(len(dbUserList), requestHashedPassword))

        for dbUser in dbUserList:

            logger.info("Authentication Login dbUser %s requestUser %s pwd %s" % (dbUser.username,requestUser,requestHashedPassword))

            #if user not found then continue
            if dbUser.username.lower() != requestUser.lower():
                msg = " Authentication Login USER NOT MATCH. i=%s continue..." % (i)
                logger.info(msg)
                i = i+1
                continue
            else:
                response = HttpResponse(json.dumps({
                     "message": "Correct password",
                     "credentialId": dbUser.partyId.partyId,
                     "secretKey": Credential.generateSecretKey(str(dbUser.partyId.partyId), dbUser.password),
                     "email": dbUser.email,
                     "role":"librarian",
                     "username": dbUser.username,
                     "userIdentifier": dbUser.userIdentifier,
                }), status=200)
                msg=" Authentication Login USER AND PWD MATCH. dbUser=%s requestUser=%s hashedRequestPassword=%s" % (dbUser.username, requestUser, requestHashedPassword)
                logger.info(msg)
                return response

        logger.info("Authentication Login end of loop")
    #}end of if not empty list
    #if we did not return from above and we are here, then it's an error.
    #print last error msg from the loop and return 401 response
    logger.info("Authentication Login %s, %s: \n %s %s %s" % (ip, msg, requestUser, requestHashedPassword, request.GET['partnerId']))
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
      user.password = Credential.generatePasswordHash(password)
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
      data['password'] = Credential.generatePasswordHash(data['password'])
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
        requiredParams = ['email', 'partnerId']
        for param in requiredParams:
            if param not in params:
                return Response({'error':param + ' param is required.'}, status=status.HTTP_400_BAD_REQUEST)
        email = params['email']
        partnerId = params['partnerId']
        if not Credential.objects.all().filter(email=email).filter(partnerId=partnerId).exists():
            return Response({'error':'no username found.'}, status=status.HTTP_400_BAD_REQUEST)

        usernames = Credential.objects.all().filter(email=email).filter(partnerId=partnerId)
        credentialSerializer = CredentialSerializerNoPassword(usernames, many=True)

        userList = ''
        for user in credentialSerializer.data:
            userList += user['username'] + '\n'

        partnerName = Partner.objects.get(partnerId=partnerId).name

        #send email
        subject = partnerName + " Usernames for %s" % email

        message = 'You have the following ' + partnerName + ' usernames associated with %s:\n' % email + userList

        from_email = "info@phoenixbioinformatics.org"

        recipient_list = [email]
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)

        return Response(credentialSerializer.data, status=status.HTTP_200_OK)

#/credentials/checkAccountExists
def checkAccountExists(request):
  if request.method == 'GET':
    params = request.GET
    if not 'partnerId' in params:
      return HttpResponse(json.dumps({'error': 'partnerId is required.'}), status=status.HTTP_400_BAD_REQUEST)
    if not 'email' in params and not 'username' in params:
      return HttpResponse(json.dumps({'error': 'You need to provide at least an email or a username.'}), status=status.HTTP_400_BAD_REQUEST)
    partnerId = params['partnerId']
    result = {}
    if 'email' in params:
      email = params['email']
      result['emailExist'] = Credential.objects.all().filter(email=email).filter(partnerId=partnerId).exists()
    if 'username' in params:
      username = params['username']
      result['usernameExist'] = Credential.objects.all().filter(username=username).filter(partnerId=partnerId).exists()
    return HttpResponse(json.dumps(result), status=status.HTTP_200_OK);


