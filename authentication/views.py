from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.core.mail import send_mail
from django.http import JsonResponse

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
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from authentication.models import Credential, GooglePartyAffiliation, Credential, OrcidCredentials
from authentication.serializers import CredentialSerializer, CredentialSerializerNoPassword
from subscription.models import Party
from partner.models import Partner
from party.serializers import PartySerializer
from party.models import Party, Country

from common.permissions import isPhoenix
from django.conf import settings

# CIPRES-13: add password decryption
from common.utils.cipresUtils import AESCipher

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
      # CIPRES-13: Decrypt user password
      if 'partnerId' not in data:
        return Response({'error': 'partnerId is required'}, status=status.HTTP_400_BAD_REQUEST)
      partnerId = data['partnerId']
      if partnerId == 'cipres':
        cipher = AESCipher()
        try:
          decryptedPassword = cipher.decrypt(data['password'])
        except Exception as e:
          return Response({'error': 'Cannot parse password: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
          pass
        data['password'] = hashlib.sha1(decryptedPassword.encode(cipher.charset)).hexdigest()
      else:
        data['password'] = hashlib.sha1(data['password'].encode('utf-8')).hexdigest()
      # CIPRES-13 end
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
        if 'name' in data:
          name = data['name']
        elif 'username' in data:
          name = data['username']
        else:
          return Response({'error': 'username is required'}, status=status.HTTP_400_BAD_REQUEST)
        if 'display' not in data:#PW-272 
          display = '0'
        else:
          display = data['display']
        # CIPRES-13: Require country info for user registration
        if partnerId == 'cipres':
          if 'countryCode' not in data:
            return Response({'error': 'countryCode is required'}, status=status.HTTP_400_BAD_REQUEST)
          else:
            countryCode = data['countryCode'].strip()
            try:
              country = Country.objects.get(abbreviation=countryCode)
            except Exception as e:
              return Response({'error': 'Cannot find country %s: %s' % (countryCode, str(e))}, status=status.HTTP_400_BAD_REQUEST)
            partyData = {'name':name, 'partyType':'user','display':display,'country':country.countryId}
        else:
          partyData = {'name':name, 'partyType':'user','display':display}
        # CIPRES-13 end
        # CYV-32: check unique constraint on username + partyId
        userAccount = Credential.objects.all().filter(username = name, partnerId = partnerId)
        if len(userAccount) > 0:
          return Response({'error': 'Combination of %s + %s already exists' % (name, partnerId)}, status=status.HTTP_400_BAD_REQUEST) 
        # CYV-32 end
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
    partnerId = self.request.GET['partnerId']
    # CIPRES-13: Decrypt user password
    if 'password' in data:
      if partnerId == 'cipres':
        cipher = AESCipher()
        try:
          decryptedPassword = cipher.decrypt(data['password'])
        except Exception as e:
          return Response({'error': 'Cannot parse password: ' + str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
          pass
        data['password'] = hashlib.sha1(decryptedPassword.encode(cipher.charset)).hexdigest()
      else:
        data['password'] = hashlib.sha1(data['password'].encode("utf-8")).hexdigest()
    # CIPRES-13 end
    # CIPRES-26: Allow update of country code
    if partnerId == 'cipres' and 'countryCode' in data:
      countryCode = data['countryCode'].strip()
      try:
        country = Country.objects.get(abbreviation=countryCode)
        partyObj = obj.partyId
        partySerializer = PartySerializer(partyObj, data={'country':country.countryId}, partial =True)
        if partySerializer.is_valid():
          partySerializer.save()
      except Exception as e:
        return Response({'error': 'Cannot find country %s: %s ' % (countryCode, str(e))}, status=status.HTTP_400_BAD_REQUEST)
    # CIPRES-26 end
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

    partnerId = request.GET.get('partnerId')
    requestPassword = request.POST.get('password')
    # CIPRES-47: handles UTF-8 passwords
    if partnerId == 'cipres':
      requestHashedPassword = hashlib.sha1(requestPassword.encode('utf-8')).hexdigest()
    else:
      requestHashedPassword = hashlib.sha1(requestPassword.encode('utf-8')).hexdigest()
    requestUser = request.POST.get('user')

    # iexact does not work unfortunately. Steve to find out why
    #dbUserList = Credential.objects.filter(partnerId=request.GET.get('partnerId')).filter(username__iexact=requestUser)

    # get list of users by partner and pwd -  less efficient though than fetching by (partner+username) as there could be many users with same pwd
    # more efficient is to fetch by partner+username

    dbUserList = Credential.objects.filter(partnerId=partnerId).filter(password=requestHashedPassword)

    i=0
    if not dbUserList.exists():

        msg = "PWD NOT FOUND IN DB. username existance unknown"
        logger.info("Authentication Login %s, %s: %s %s %s" % (ip, msg, requestUser, requestHashedPassword, request.GET['partnerId']))
        return HttpResponse(json.dumps({"message":msg}), status=401)

    else:

        logger.info("Authentication Login %s USER(S) WITH PWD %s FOUND:" %(len(dbUserList), requestHashedPassword))

        for dbUser in dbUserList:

            # logger.info("Authentication Login dbUser %s requestUser %s pwd %s" % (dbUser.username,requestUser,requestHashedPassword))

            #if user not found then continue
            if dbUser.username.lower() != requestUser.lower():
                msg = " Authentication Login USER NOT MATCH. i=%s continue..." % (i)
                logger.info(msg)
                i = i+1
                continue
            else:
                #CIPRES-21: retrieve abbreviation code of the user country when the user logs in
                countryAbbr = ""
                country = dbUser.partyId.country
                if country:
                  countryAbbr = country.abbreviation
                response = HttpResponse(json.dumps({
                     "message": "Correct password",
                     "credentialId": dbUser.partyId.partyId,
                     "secretKey": generateSecretKey(str(dbUser.partyId.partyId), dbUser.password),
                     "email": dbUser.email,
                     "role":"librarian",
                     "username": dbUser.username,
                     "userIdentifier": dbUser.userIdentifier,
                     "countryCode": countryAbbr
                }), status=200)
                msg=" Authentication Login USER AND PWD MATCH. dbUser=%s requestUser=%s hashedRequestPassword=%s" % (dbUser.username, requestUser, requestHashedPassword)
                logger.info(msg)
                return response

        # logger.info("Authentication Login end of loop")
    #}end of if not empty list
    #if we did not return from above and we are here, then it's an error.
    #print last error msg from the loop and return 401 response
    logger.info("Authentication Login %s, %s: \n %s %s %s" % (ip, msg, requestUser, requestHashedPassword, request.GET['partnerId']))
    return HttpResponse(json.dumps({"message":msg}), status=401)

#/credentials/resetPwd/
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

#/credentials/checkOrcid
class CheckOrcid(generics.GenericAPIView):
    requireApiKey = False
    queryset = Credential.objects.all()
    
    def get_queryset(self):
        user_identifier = self.request.query_params.get('userIdentifier')
        partner_id = self.request.query_params.get('partnerId')
        return self.queryset.filter(userIdentifier=user_identifier, partnerId__partnerId=partner_id)

    def get(self, request, *args, **kwargs):
        user_identifier = request.query_params.get('userIdentifier')
        partner_id = request.query_params.get('partnerId')

        if not user_identifier or not partner_id:
            return Response({'error': 'Both userIdentifier and partnerId are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if partner_id.lower() != 'tair':
            return Response({'error': 'This check is only available for TAIR users.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            credential = self.get_queryset().get()
        except Credential.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            orcid_credential = OrcidCredentials.objects.get(
                credential=credential,
                orcid_id__isnull=False
            )
            has_orcid = True
            orcid_id = orcid_credential.orcid_id
        except OrcidCredentials.DoesNotExist:
            has_orcid = False
            orcid_id = None

        return Response({
            'has_orcid': has_orcid,
            'orcid_id': orcid_id
        })

checkOrcid = CheckOrcid.as_view()
    
#/credentials/getUserIdentifierByOrcid
class GetUserIdentifierByOrcid(generics.GenericAPIView):
    requireApiKey = False
    queryset = OrcidCredentials.objects.all()

    def get_queryset(self):
        orcid_id = self.request.query_params.get('orcidId')
        return self.queryset.filter(orcid_id=orcid_id)

    def get(self, request, *args, **kwargs):
        orcid_id = request.query_params.get('orcidId')
        
        if not orcid_id:
            return Response({'error': 'ORCID ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            orcid_credential = self.get_queryset().get()
            user_identifier = orcid_credential.credential.userIdentifier
            return Response({'userIdentifier': user_identifier})
        except OrcidCredentials.DoesNotExist:
            return Response({'userIdentifier': None})

getUserIdentifierByOrcid = GetUserIdentifierByOrcid.as_view()


#/credentials/addOrcidCredentials
class AddOrcidCredentials(generics.GenericAPIView):
    requireApiKey = False
    queryset = Credential.objects.all()

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(AddOrcidCredentials, self).dispatch(*args, **kwargs)

    def get_data(self, request):
        logging.info("Received request to addOrcidCredentials")
        logging.info("Request method: %s", request.method)
        logging.info("Request GET params: %s", request.GET)

        # Try to get data from query parameters first
        data = request.GET.dict()
        
        # If not in query params, check content type and parse accordingly
        if not data:
            if request.content_type == 'application/json':
                try:
                    data = json.loads(request.body)
                except ValueError:
                    logging.error("Invalid JSON in request body")
                    data = {}
            else:
                data = request.POST.dict()
        
        logging.info("Parsed request data: %s", data)
        return data

    def post(self, request, *args, **kwargs):
        data = self.get_data(request)

        secretKey = data.get('secretKey')
        credentialId = data.get('credentialId')
        orcid_id = data.get('orcidId')
        orcid_access_token = data.get('orcidAccessToken')
        orcid_refresh_token = data.get('orcidRefreshToken')


        if not all([secretKey, credentialId, orcid_id, orcid_access_token, orcid_refresh_token]):
            logging.error("Missing required fields. Received: %s", data)
            return Response({'success': False, 'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        loggedIn = Credential.validate(credentialId, secretKey)

        if not loggedIn:
            logging.error("Invalid credentials provided")
            return Response({'success': False, 'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            credential = Credential.objects.get(partyId=credentialId, partnerId='tair')
        except Credential.DoesNotExist:
            logging.error("User not found: %s", credentialId)
            return Response({'success': False, 'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if ORCID credentials already exist for this user
        orcid_cred, created = OrcidCredentials.objects.update_or_create(
            credential=credential,
            defaults={
                'orcid_id': orcid_id,
                'orcid_access_token': orcid_access_token,
                'orcid_refresh_token': orcid_refresh_token
            }
        )
        logging.info("ORCID credentials %s for user: %s", 'created' if created else 'updated', credentialId)

        return Response({'success': True, 'message': 'ORCID credentials added successfully'})

addOrcidCredentials = AddOrcidCredentials.as_view()



class AuthenticateOrcid(APIView):
    requireApiKey = False

    def post(self, request):
        logger.info("Received ORCID authentication request")
        auth_code = request.data.get('code')
        if not auth_code:
            logger.warning("Auth code is missing in the request")
            return Response({'message': 'Auth code is required.'}, status=status.HTTP_400_BAD_REQUEST)

        logger.info("Exchanging auth code for ORCID ID")
        token_url = "{0}/oauth/token".format(settings.ORCID_DOMAIN)
        data = {
            'client_id': settings.ORCID_CLIENT_ID,
            'client_secret': settings.ORCID_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': settings.ORCID_REDIRECT_URL,
        }
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        try:
            logger.debug("Sending request to ORCID API: URL=%s, Headers=%s, Data=%s", token_url, headers, data)
            response = requests.post(token_url, data=data, headers=headers)
            logger.info("Received response from ORCID API: Status=%s", response.status_code)
            logger.debug("ORCID API response content: %s", response.text)
            response.raise_for_status()
            token_data = response.json()
            orcid_id = token_data['orcid']
            orcid_access_token = token_data['access_token']
            orcid_refresh_token = token_data['refresh_token']
            logger.info("Successfully obtained ORCID ID: %s", orcid_id)
        except requests.RequestException as e:
            logger.error("Failed to authenticate with ORCID: %s", str(e))
            return Response({'message': 'Failed to authenticate with ORCID.'}, status=status.HTTP_400_BAD_REQUEST)

        logger.info("Getting user identifier for ORCID ID: %s", orcid_id)
        
        try:
            orcid_credentials = OrcidCredentials.objects.get(orcid_id=orcid_id)
        except OrcidCredentials.DoesNotExist:
            logger.warning("No user found for ORCID ID: %s", orcid_id)
            return Response({'message': 'No such user'}, status=status.HTTP_401_UNAUTHORIZED)

        credential = orcid_credentials.credential
        logger.info("Updating ORCID credentials")
        orcid_credentials.orcid_access_token = orcid_access_token
        orcid_credentials.orcid_refresh_token = orcid_refresh_token
        orcid_credentials.save()
        logger.info("ORCID credentials updated successfully")

        logger.info("Generating secret key")
        secret_key = base64.b64encode(
            hmac.new(
                str(credential.partyId.partyId),
                credential.password,
                hashlib.sha1
            ).digest()
        )

        country_code = ""
        if credential.partyId.country:
            country_code = credential.partyId.country.abbreviation
        logger.info("Country code retrieved: %s", country_code)

        logger.info("Preparing response")
        response_data = {
            "message": "Correct password",
            "credentialId": credential.partyId.partyId,
            "secretKey": secret_key,
            "email": credential.email,
            "role": "librarian",
            "username": credential.username,
            "userIdentifier": credential.userIdentifier,
            "countryCode": country_code
        }
        logger.info("Authentication successful for user: %s", credential.username)
        return Response(response_data, status=status.HTTP_200_OK)

authenticateOrcid = AuthenticateOrcid.as_view()


#/credentials/unlinkOrcid
class UnlinkOrcid(generics.GenericAPIView):
    requireApiKey = False
    queryset = Credential.objects.all()

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(UnlinkOrcid, self).dispatch(*args, **kwargs)

    def get_data(self, request):
        logging.info("Received request to unlinkOrcid")
        logging.info("Request method: %s", request.method)
        logging.info("Request GET params: %s", request.GET)

        # Try to get data from query parameters first
        data = request.GET.dict()
        
        # If not in query params, check content type and parse accordingly
        if not data:
            if request.content_type == 'application/json':
                try:
                    data = json.loads(request.body)
                except ValueError:
                    logging.error("Invalid JSON in request body")
                    data = {}
            else:
                data = request.POST.dict()
        
        logging.info("Parsed request data: %s", data)
        return data

    def post(self, request, *args, **kwargs):
        data = self.get_data(request)

        secretKey = data.get('secretKey')
        credentialId = data.get('credentialId')

        if not all([secretKey, credentialId]):
            logging.error("Missing required fields. Received: %s", data)
            return Response({
                'success': False, 
                'error': 'Missing required fields'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate the user's credentials
        loggedIn = Credential.validate(credentialId, secretKey)

        if not loggedIn:
            logging.error("Invalid credentials provided")
            return Response({
                'success': False, 
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            # Get the credential object
            credential = Credential.objects.get(partyId=credentialId, partnerId='tair')
            
            # Update the OrcidCredentials record
            result = OrcidCredentials.objects.filter(credential=credential).update(
                orcid_id=None,
                orcid_access_token=None,
                orcid_refresh_token=None
            )
            
            if result > 0:
                logging.info("Successfully unlinked ORCID credentials for user: %s", credentialId)
                return Response({
                    'success': True,
                    'message': 'ORCID credentials successfully unlinked'
                })
            else:
                logging.warning("No ORCID credentials found to unlink for user: %s", credentialId)
                return Response({
                    'success': False,
                    'error': 'No ORCID credentials found to unlink'
                }, status=status.HTTP_404_NOT_FOUND)

        except Credential.DoesNotExist:
            logging.error("User not found: %s", credentialId)
            return Response({
                'success': False,
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logging.error("Error unlinking ORCID credentials: %s", str(e))
            return Response({
                'success': False,
                'error': 'Internal server error while unlinking ORCID credentials'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

unlinkOrcid = UnlinkOrcid.as_view()