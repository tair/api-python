#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.http import HttpResponse, StreamingHttpResponse

from subscription.controls import PaymentControl, SubscriptionControl
from subscription.models import *
from subscription.serializers import *

from partner.models import Partner, SubscriptionTerm
from party.models import Party, ImageInfo
from party.serializers import PartySerializer
from authentication.models import Credential
from authentication.serializers import CredentialSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from common.views import GenericCRUDView
from common.permissions import isPhoenix
from common.common import getRemoteIpAddress
from common.utils.cyverseUtils import CyVerseClient

from django.shortcuts import render
from django.utils.encoding import smart_str

import stripe
import json
import random, string
import hashlib
import datetime
import csv

from django.conf import settings

from django.core.mail import send_mail

from django.utils import timezone

import uuid

import logging
logger = logging.getLogger('phoenix.api.subscription')

# top level: /subscriptions/

# Basic CRUD operation for Subscriptions, and SubscriptionTransactions

# /
class SubscriptionCRUD(GenericCRUDView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    requireApiKey = False

    def get(self, request):
        params = request.GET
        if 'subscriptionId' in request.GET:
            subscriptionId = request.GET.get('subscriptionId')
            subscription = Subscription.objects.all().get(subscriptionId=subscriptionId)
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data)
        elif 'partyId' in params:
            partyId = params['partyId']
            now = datetime.datetime.now()
            if 'checkConsortium' in params and params['checkConsortium'] == 'true':
                partnerIdList = Partner.objects.all().values_list('partnerId', flat=True)
                idSub = []
                allSub = Subscription.getById(partyId)
                for partnerId in partnerIdList:
                    if allSub.filter(partnerId=partnerId).filter(endDate__gt=now).filter(startDate__lt=now).exists():
                        idSub.append(allSub.filter(partnerId=partnerId).filter(endDate__gt=now).filter(startDate__lt=now).latest('endDate'))
                serializer = SubscriptionSerializer(idSub, many=True)
            elif 'active' in params and params['active'] == 'true':
                activeSubscriptions = Subscription.objects.all().filter(partyId=partyId).filter(endDate__gt=now).filter(startDate__lt=now)
                serializer = SubscriptionSerializer(activeSubscriptions, many=True)
            else:
                allSubscriptions = Subscription.objects.all().filter(partyId=partyId)
                serializer = SubscriptionSerializer(allSubscriptions, many=True)
            return Response(serializer.data, status=200)
        elif all(param in params for param in ['partnerId', 'ipAddress', 'userIdentifier']):
            partnerId = params['partnerId']
            ipAddress = params['ipAddress']
            userIdentifier = params['userIdentifier']
            idSub = None #Pw-418
            subList = [] #Pw-418
            ipSub = Subscription.getByIp(ipAddress).filter(partnerId=partnerId)
            if Credential.objects.filter(userIdentifier=userIdentifier).filter(partnerId=partnerId).exists():
                partyId = Credential.objects.filter(partnerId=partnerId).filter(userIdentifier=userIdentifier)[0].partyId.partyId
                idSub = Subscription.getById(partyId).filter(partnerId=partnerId)
            if (idSub):
                subList = SubscriptionSerializer(ipSub, many=True).data+SubscriptionSerializer(idSub, many=True).data
            else:
                subList = SubscriptionSerializer(ipSub, many=True).data
            for sub in subList:
                if Party.objects.filter(partyId = sub['partyId']).exists():
                    party = PartySerializer(Party.objects.get(partyId = sub['partyId'])).data
                    sub['partyType'] = party['partyType']
                    sub['name'] = party['name']
            return HttpResponse(json.dumps(subList), content_type="application/json")
        else:
            return Response({"error":"Essential parameters needed."}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        if isPhoenix(self.request):
            partyId = self.request.GET.get('partyId')
            return super(SubscriptionCRUD, self).get_queryset().filter(partyId=partyId)
        return []

    # overrides default POST to create a subscription transaction
    def post(self, request):
        if ('activationCode' in request.data):
            # subscription creation by activation code
            if not ActivationCode.objects.filter(activationCode=request.data['activationCode']).exists():
                return Response({"message":"incorrect activation code"}, status=status.HTTP_400_BAD_REQUEST)
            activationCodeObj = ActivationCode.objects.get(activationCode=request.data['activationCode'])
            if not activationCodeObj.partyId == None:
                return Response({"message":"activation code is already used"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                partyId = request.data['partyId']
                partnerId = activationCodeObj.partnerId.partnerId
                period = activationCodeObj.period
                # retrive and update existing subscription, or creat a new one if partner/party does
                # not already have one.
                (subscription, transactionType, transactionStartDate, transactionEndDate) = SubscriptionControl.createOrUpdateSubscription(partyId, partnerId, period)
            except Exception:
                return Response('failed to create or update subscription')
            try:
                # get transactionType from activationCode
                transactionType = activationCodeObj.transactionType
                subscription.save()
                transaction = SubscriptionTransaction.createFromSubscription(subscription, transactionType, transactionStartDate, transactionEndDate)
            except Exception:
                return Response('failed to create transaction')

            try:
                # set activationCodeObj to be used.
                partyObj = Party.objects.get(partyId=partyId)
            except Exception:
                return Response('failed to get partyObj')
            try:
                activationCodeObj.partyId = partyObj
            except Exception:
                return Response('failed to assign partyObj')
            try:
                activationCodeObj.save()
            except Exception:
                return Response('failed to save activationCodeObj')

            serializer = self.serializer_class(subscription)
            returnData = serializer.data
            returnData['subscriptionTransactionId']=transaction.subscriptionTransactionId
            return Response(returnData, status=status.HTTP_201_CREATED)
        else:
            # basic subscription creation
            if not isPhoenix(self.request):
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                subscription = serializer.save()
                transaction = SubscriptionTransaction.createFromSubscription(subscription, 'create')
                returnData = serializer.data
                returnData['subscriptionTransactionId']=transaction.subscriptionTransactionId
                return Response(returnData, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# /transactions/
class SubscriptionTransactionCRUD(GenericCRUDView):
    queryset = SubscriptionTransaction.objects.all()
    serializer_class = SubscriptionTransactionSerializer

#------------------- End of Basic CRUD operations --------------


# Specific queries

# /<pk>/renewal/
class SubscriptionRenewal(generics.GenericAPIView):
    requireApiKey = False
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def put(self, request, pk):
        subscription = Subscription.objects.get(subscriptionId=pk)
        serializer = SubscriptionSerializer(subscription, data=request.data)
        if serializer.is_valid():
            subscription = serializer.save()
            transaction = SubscriptionTransaction.createFromSubscription(subscription, 'renew')
            returnData = serializer.data
            returnData['subscriptionTransactionId']=transaction.subscriptionTransactionId
            return Response(returnData)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# /payments/
class SubscriptionsPayment(APIView):
    requireApiKey = False

    def get(self, request):
        message = {}
        if (not PaymentControl.isValidRequest(request, message)):
            return HttpResponse(message['message'], 400)
        #Currently assumes that subscription objects in database stores price in cents
        #TODO: Handle more human readable price
        termId = request.GET.get('termId')
        message['price'] = int(SubscriptionTerm.objects.get(subscriptionTermId=termId).price)
        message['quantity'] = request.GET.get('quantity')
        message['termId'] = termId
        message['stripeKey'] = settings.STRIPE_PUBLIC_KEY
        return render(request, "subscription/paymentIndex.html", message)

    def post(self, request):
        stripe_api_secret_test_key = settings.STRIPE_PRIVATE_KEY
        stripe.api_key = stripe_api_secret_test_key
        token = request.POST['stripeToken']
        price = float(request.POST['price'])
        termId = request.POST['termId']
        quantity = int(request.POST['quantity'])
        email = request.POST['email']
        firstname = request.POST['firstName']
        lastname = request.POST['lastName']
        institute = request.POST['institute']
        street = request.POST['street']
        city = request.POST['city']
        state = request.POST['state']
        country = request.POST['country']
        zip = request.POST['zip']
        hostname = request.META.get("HTTP_ORIGIN")
        redirect = request.POST['redirect']
        other = request.POST['other'] #PW-248. Let it be in two places - in descriptionPartnerDuration and in email body
        #PW-204 requirement: "TAIR 1-year subscription" would suffice.
        descriptionDuration = SubscriptionTerm.objects.get(subscriptionTermId=termId).description
        partnerName = SubscriptionTerm.objects.get(subscriptionTermId=termId).partnerId.name
        descriptionPartnerDuration = '%s %s subscription other: %s name: %s %s'%(partnerName,descriptionDuration,other,firstname,lastname)
        domain = request.POST['domain']

        message = PaymentControl.tryCharge(stripe_api_secret_test_key, token, price, partnerName, descriptionPartnerDuration, termId, quantity, email, firstname, lastname, institute, street, city, state, country, zip, hostname, redirect, other, domain)
        #PW-120 vet
        status = 200
        if 'message' in message:
            status = 400
        return HttpResponse(json.dumps(message), content_type="application/json", status=status)

# /institutions/
class InstitutionSubscription(APIView):
    requireApiKey = False
    def post (self, request):
        data = request.data
        dataTuple = (
            data.get('comments'),
            data.get('firstName'),
            data.get('lastName'),
            data.get('email'),
            data.get('institution'),
            data.get('librarianName'),
            data.get('librarianEmail'),
        )

        subject = "%s Institutional Subscription Request For %s" % (data.get('partnerName'), data.get('institution'))
        message = "%s\n" \
                  "\n" \
                 "My information is below.\n" \
                  "First Name: %s\n" \
                  "Last Name: %s \n" \
                  "Email: %s \n" \
                  "Institution Name: %s \n" \
                  "\n" \
                  "My library contact information is below.\n" \
                  "Librarian Contact Name: %s \n" \
                  "Librarian Email: %s \n" \
                  % dataTuple

        message += "\nSubmitter's public IP Address: " + getRemoteIpAddress(request)

#        logging.basicConfig(filename="/home/ec2-user/logs/debug.log",
#                            format='%(asctime)s %(message)s'
#        )
#        logger.info("------Sending institution subscription email------")
#        logger.info("%s" % subject)
#        logger.info("%s" % message)

        from_email = "subscriptions@phoenixbioinformatics.org"
        recipient_list = ["subscriptions@phoenixbioinformatics.org"]
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
#        logger.info("------Done sending institution subscription email------")

        return HttpResponse(json.dumps({'message':'success'}), content_type="application/json")

# /commercials/
class CommercialSubscription(APIView):
    requireApiKey = False
    def post (self, request):
        data = request.data
        dataTuple = (
            data.get('comments'),
            data.get('firstName'),
            data.get('lastName'),
            data.get('email'),
            data.get('institution'),
        )

        subject = "%s Commercial Subscription Request For %s" % (data.get('partnerName'), data.get('institution'))
        message = "%s\n" \
                  "\n" \
                  "Please contact me about a commercial subscription. My information is below.\n" \
                  "First Name: %s\n" \
                  "Last Name: %s \n" \
                  "Email: %s \n" \
                  "Company Name: %s \n" \
                  "\n" \
                  "I am interested in: \n" \
                  % dataTuple

        if data.get('individualLicense') == 'true':
            message += "Individual Licenses\n"
        if data.get('companyLicense') == 'true':
            message += "Company Licenses\n"

        message += "\nSubmitter's public IP Address: " + getRemoteIpAddress(request)

#        logging.basicConfig(filename="/home/ec2-user/logs/debug.log",
#                            format='%(asctime)s %(message)s'
#        )
#        logger.info("------Sending commercial subscription email------")
#        logger.info("%s" % subject)
#        logger.info("%s" % message)

        from_email = "subscriptions@phoenixbioinformatics.org"
        recipient_list = ["subscriptions@phoenixbioinformatics.org"]
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
#        logger.info("------Done sending commercial email------")
        return HttpResponse(json.dumps({'message':'success'}), content_type="application/json")

# /enddate
# Among all the subscriptions to a given partner, looks for the effective subscription that either covers the given IP address or belongs to the given party.
# Upon success, returns the expiration date of the found subscription and 'subscribed' status as True; otherwise, the returned expiration date is null and status is False.
class EndDate(generics.GenericAPIView):
    requireApiKey = False
    def get(self, request):
        partnerId=request.GET.get("partnerId")
        if 'ipAddress' in request.GET:
            ipAddress=request.GET.get("ipAddress")
        else:
            ipAddress=getRemoteIpAddress(request)
        partyId = None
        if 'partyId' in request.GET:
            partyId = request.GET.get('partyId')
        elif 'userIdentifier' in request.GET:
            userIdentifier=request.GET.get("userIdentifier")
        else:
            return Response({'error':'partyId or userIdentifier is required'}, status=status.HTTP_400_BAD_REQUEST)
        expDate = ""
        subscribed = False
        ipSub = Subscription.getActiveByIp(ipAddress, partnerId)
        idSub = None #Pw-418
        subList = [] #Pw-418
        subscriptionType = None
        if not partyId:
            if Credential.objects.filter(userIdentifier=userIdentifier).filter(partnerId=partnerId).exists():
                partyId = Credential.objects.filter(partnerId=partnerId).filter(userIdentifier=userIdentifier)[0].partyId.partyId
                idSub = Subscription.getActiveById(partyId, partnerId)
        else:
            try:
                idSub = Subscription.getActiveById(partyId, partnerId)
            except:
                return Response({'error':'getting active susbcription by id failed'}, status=status.HTTP_400_BAD_REQUEST)
        if (idSub):
            subList = SubscriptionSerializer(ipSub, many=True).data+SubscriptionSerializer(idSub, many=True).data
        else:
            subList = SubscriptionSerializer(ipSub, many=True).data
        if subList != []:
            subscribed = True
            expDate = max(sub['endDate'] for sub in subList)
            if ipSub:
                subscriptionType = 'institutional'
            elif idSub:
                subscriptionType = 'individual'
        return HttpResponse(json.dumps({'expDate':expDate, 'subscribed':subscribed, 'subscriptionType':subscriptionType}), content_type="application/json")

# /activesubscriptions/<partyId>
class ActiveSubscriptions(generics.GenericAPIView):
    requireApiKey = False
    def get(self, request, partyId):
        now = datetime.datetime.now()
        activeSubscriptions = Subscription.objects.all().filter(partyId=partyId).filter(endDate__gt=now).filter(startDate__lt=now)
        serializer = SubscriptionSerializer(activeSubscriptions, many=True)
    #return HttpResponse(json.dumps(dict(serializer.data)))
        ret = {}
        for s in serializer.data:
            ret[s['partnerId']] = dict(s)
        return HttpResponse(json.dumps(ret), status=200)

# /allsubscriptions/<partyId>
class AllSubscriptions(generics.GenericAPIView):
    requireApiKey = False
    def get(self, request, partyId):
        allSubscriptions = Subscription.objects.all().filter(partyId=partyId)
        serializer = SubscriptionSerializer(allSubscriptions, many=True)
        #return HttpResponse(json.dumps(dict(serializer.data)))
        ret = {}
        for s in serializer.data:
            ret[s['partnerId']] = dict(s)
        return HttpResponse(json.dumps(ret), status=200)

# /consortiums/
class ConsortiumSubscriptions(generics.GenericAPIView):
    requireApiKey = False
    def get(self, request):
        params = request.GET
        if not 'partyId' in params:
            return Response({'error':'partyId is required'}, status=status.HTTP_400_BAD_REQUEST)
        ret = {}
        now = datetime.datetime.now()
        partyId = params['partyId']
        if 'active' in params and params['active'] == 'true':
            if Party.objects.all().get(partyId=partyId):
                consortiums = Party.objects.all().get(partyId=partyId).consortiums.all()
                for consortium in consortiums:
                    consortiumActiveSubscriptions = Subscription.objects.all().filter(partyId=consortium.partyId).filter(endDate__gt=now).filter(startDate__lt=now)
                    serializer = SubscriptionSerializer(consortiumActiveSubscriptions, many=True)
                    partySerializer = PartySerializer(consortium)
                    for s in serializer.data:
                        if s['partnerId'] in ret:
                            ret[s['partnerId']].append(partySerializer.data)
                        else:
                            ret[s['partnerId']] = []
                            ret[s['partnerId']].append(partySerializer.data)
        return Response(ret, status=200)

# /consactsubscriptions/<partyId>
class ConsActSubscriptions(generics.GenericAPIView):
    requireApiKey = False
    def get(self, request, partyId):
        ret = {}
        now = datetime.datetime.now()
        if Party.objects.all().get(partyId=partyId):
            consortiums = Party.objects.all().get(partyId=partyId).consortiums.all()
            for consortium in consortiums:
                consortiumActiveSubscriptions = Subscription.objects.all().filter(partyId=consortium.partyId).filter(endDate__gt=now).filter(startDate__lt=now)
                serializer = SubscriptionSerializer(consortiumActiveSubscriptions, many=True)
                partySerializer = PartySerializer(consortium)
                for s in serializer.data:
                    if s['partnerId'] in ret:
                        ret[s['partnerId']].append(partySerializer.data)
                    else:
                        ret[s['partnerId']] = []
                        ret[s['partnerId']].append(partySerializer.data)
        return HttpResponse(json.dumps(ret), status=200)

# /renew/
class RenewSubscription(generics.GenericAPIView):
    requireApiKey = False
    def post(self, request):
        if not isPhoenix(request):
           return HttpResponse(status=400)
        data = request.data
        subject = "%s Subscription Renewal Request For %s" % (data['partnerName'], data['partyName'])
        message = "\n" \
                  "\n" \
                  "Please contact me about a subscription renewal. My information is below.\n" \
                  "Product: %s\n" \
                  "Email: %s \n" \
                  "%s: %s \n" \
                  "Comments: %s \n" \
                  "\n" \
                  % (data['partnerName'], data['email'], data['partyType'], data['partyName'], data['comments'])
        from_email = "subscriptions@phoenixbioinformatics.org"
        recipient_list = ["subscriptions@phoenixbioinformatics.org"]
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
        return HttpResponse(json.dumps({'message':'success'}), content_type="application/json")

# /request/
class RequestSubscription(generics.GenericAPIView):
    requireApiKey = False
    def post(self, request):
        if not isPhoenix(request):
           return HttpResponse(status=400)
        data = request.data
        subject = "%s Subscription Request For %s" % (data['partnerName'], data['partyName'])
        message = "\n" \
                  "\n" \
                  "Please contact me about a subscription request. My information is below.\n" \
                  "Product: %s\n" \
                  "Email: %s \n" \
                  "%s: %s \n" \
                  "Comments: %s \n" \
                  "\n" \
                  % (data['partnerName'], data['email'], data['partyType'], data['partyName'], data['comments'])
        from_email = "subscriptions@phoenixbioinformatics.org"
        recipient_list = ["subscriptions@phoenixbioinformatics.org"]
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
        return HttpResponse(json.dumps({'message':'success'}), content_type="application/json")

class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

# /subscriptionrequest
class SubscriptionRequestCRUD(GenericCRUDView):
    queryset = SubscriptionRequest.objects.all()
    serializer_class = SubscriptionRequestSerializer
    requireApiKey = False

    def get(self, request):
        allSubscriptionRequests = SubscriptionRequest.objects.all()
        serializer = self.serializer_class(allSubscriptionRequests, many=True)
        # This part comes from django documentation on large csv file generation:
        # https://docs.djangoproject.com/en/1.10/howto/outputting-csv/#streaming-large-csv-files
        requestJSONList = serializer.data
        # preprocessing requestDate
        for request in requestJSONList:
            request['requestDate'] = datetime.datetime.strptime(request['requestDate'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%m/%d/%Y')
        rows = [request.values() for request in requestJSONList]
        try:
            header = requestJSONList[0].keys()
        except:
            return Response("requestJSONList[0] index out of range")
        rows.insert(0, header)
        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        response = StreamingHttpResponse((writer.writerow(row) for row in rows),content_type="text/csv")
        now = datetime.datetime.now()
        response['Content-Disposition'] = 'attachment; filename="requests_report_{:%Y-%m-%d_%H:%M}.csv"'.format(now)
        response['X-Sendfile'] = smart_str('/Downloads')
        return response

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({'error':'serializer error'}, status=status.HTTP_400_BAD_REQUEST)

#active/
class SubscriptionActiveCRUD(APIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    requireApiKey = False

    def get(self,request):
        params = request.GET
        partnerId = params['partnerId']
        ipAddress = params['ipAddress']
        userIdentifier = params['userIdentifier']
        idSub = None #Pw-418
        subList = [] #Pw-418
        ipSub = Subscription.getActiveByIp(ipAddress, partnerId)
        if Credential.objects.filter(userIdentifier=userIdentifier).filter(partnerId=partnerId).exists():
            partyId = Credential.objects.filter(partnerId=partnerId).filter(userIdentifier=userIdentifier)[0].partyId.partyId
            idSub = Subscription.getActiveById(partyId, partnerId)
        if (idSub):
            subList = SubscriptionSerializer(ipSub, many=True).data+SubscriptionSerializer(idSub, many=True).data
        else:
            subList = SubscriptionSerializer(ipSub, many=True).data
        for sub in subList:
            if Party.objects.filter(partyId = sub['partyId']).exists():
                party = PartySerializer(Party.objects.get(partyId = sub['partyId'])).data
                sub['partyType'] = party['partyType']
                sub['name'] = party['name']
        return HttpResponse(json.dumps(subList), content_type="application/json")

# /activationCodes/
class ActivationCodeCRUD(GenericCRUDView):
    queryset = ActivationCode.objects.all()
    serializer_class = ActivationCodeSerializer
    requireApiKey = False

    def post(self,request):
        if not isPhoenix(request):
           return HttpResponse(status=400)

        quantity = int(request.GET.get('quantity'))
        period = int(request.GET.get('period'))
        partnerId = request.GET.get('partnerId')
        transactionType = request.GET.get('transactionType')
        partnerObj = Partner.objects.get(partnerId=partnerId)

        if quantity > 99:
            return []

        now = timezone.now()

        activationCodes = []

        for i in xrange(quantity):
            # create an activation code based on partnerId and period.
            activationCodeObj = ActivationCode()
            activationCodeObj.activationCode=str(uuid.uuid4())
            activationCodeObj.partnerId=partnerObj
            activationCodeObj.period=period
            activationCodeObj.partyId=None
            activationCodeObj.purchaseDate=now
            activationCodeObj.transactionType=transactionType
            activationCodeObj.save()
            activationCodes.append(activationCodeObj.activationCode)

        return HttpResponse(json.dumps(activationCodes), status=200)

    def put(self, request):
        if not isPhoenix(request):
           return HttpResponse(status=400)


        params = request.GET
        fields = ['activationCodeId', 'deleteMarker']
        for field in fields:
            if field not in params:
                return Response({"error": field + " field is needed."}, status=status.HTTP_400_BAD_REQUEST)

        activationCodeId = params['activationCodeId']
        deleteMarker = True if params['deleteMarker'] == 'true' else False

        activationCodeIdList = map(int, activationCodeId.split(','))

        activationCodes = ActivationCode.objects.all().filter(activationCodeId__in=activationCodeIdList)

        try:
            activationCodes.update(deleteMarker=deleteMarker)
        except:
            return Response({'error':'update deleteMarker error'}, status=status.HTTP_400_BAD_REQUEST)

        serializers = ActivationCodeSerializer(activationCodes, many=True)

        return Response(serializers.data, status=status.HTTP_200_OK)

# /membership
# MBANK-13: An extension of /enddate endpoint for member based subscription authentication
# Among all the subscriptions to a given partner, looks for the effective subscription that covers the given IP address
# Upon success, returns the expiration date, member name and member logo url of the found subscription 
# and 'isMember' status as True; otherwise, the returned expiration date is null and isMember status is False.
class Membership(generics.GenericAPIView):
    requireApiKey = False
    def get(self, request):
        if not 'partnerId' in request.GET:
            return Response({'error':'partnerId is required'}, status=status.HTTP_400_BAD_REQUEST)
        partnerId=request.GET.get("partnerId")
        if 'ipAddress' in request.GET:
            ipAddress=request.GET.get("ipAddress")
        else:
            ipAddress=getRemoteIpAddress(request)
        isMember = False
        expDate = ""
        name = ""
        imageUrl = ""
        ipSub = Subscription.getActiveByIp(ipAddress, partnerId)
        subList = SubscriptionSerializer(ipSub, many=True).data
        if subList != []:
            isMember = True
            for sub in subList:
                if expDate == "":
                    expDate = sub['endDate']
                else:
                    expDate = max(expDate, sub['endDate'])
                items = ImageInfo.objects.all().filter(partyId=sub['partyId'])
                if (items.exists()):
                    memberInfo = items[0]
                    name = memberInfo.name
                    imageUrl = memberInfo.imageUrl
        return HttpResponse(json.dumps({'isMember':isMember, 'expDate':expDate, "name":name, "imageUrl":imageUrl }), content_type="application/json")

# /active-usage-unit-purchase
# CIPRES-20: End point for querying a user's usage units purchased from a given number of days before till now
# params: partyId, partnerId, number of days as "activeDuration"
# returns: a list of UsageUnitPurchase records in JSON format
class ActiveUsageUnitPurchase(generics.GenericAPIView):
    requireApiKey = False
    def get(self,request):
        params = request.GET
        # not checking param existence since it is only used by Phoenix's resources
        partnerId = params['partnerId']
        partyId = params['partyId']
        duration = int(params['activeDuration'])
        activePurchases = UsageUnitPurchase.getActiveByIdAndPartner(partyId, partnerId, duration)
        serializer = UsageUnitPurchaseSerializer(activePurchases, many=True)
        return HttpResponse(json.dumps(dict(serializer.data)), content_type="application/json")

# /active-usage-unit-purchase/sum
# CIPRES-20: End point for querying the sum of a user's usage units purchased from a given number of days before till now
# params: partyId, partnerId, number of days as "activeDuration"
# returns: the sum of quantity of the matching UsageUnitPurchase records in JSON format as "totalActivePurchasedUnit"
class ActiveUsageUnitPurchaseSum(generics.GenericAPIView):
    requireApiKey = False
    def get(self,request):
        params = request.GET
        # not checking param existence since it is only used by Phoenix's resources
        partnerId = params['partnerId']
        partyId = params['partyId']
        duration = int(params['activeDuration'])
        totalActiveUnit = UsageUnitPurchase.getActiveUnitSumByIdAndPartner(partyId, partnerId, duration)
        return HttpResponse(json.dumps({'totalActivePurchasedUnit': totalActiveUnit}), content_type="application/json")

# /payments/usage-unit
# CIPRES-10: End point for posting payment for CIPRES
class UsageUnitsPayment(APIView):
    requireApiKey = False

    def get(self, request):
        message = {}
        if (not PaymentControl.isValidRequest(request, message)):
            return HttpResponse(message['message'], 400)
        #Currently assumes that subscription objects in database stores price in dollars
        #TODO: Handle more human readable price
        termId = request.GET.get('termId')
        message['price'] = int(SubscriptionTerm.objects.get(subscriptionTermId=termId).price)
        message['quantity'] = request.GET.get('quantity')
        message['termId'] = termId
        message['stripeKey'] = settings.STRIPE_PUBLIC_KEY
        return render(request, "subscription/paymentIndex.html", message)

    def post(self, request):
        stripe_api_secret_test_key = settings.STRIPE_PRIVATE_KEY
        stripe.api_key = stripe_api_secret_test_key
        partyId = request.POST['partyId']
        userIdentifier = request.POST['userIdentifier']
        token = request.POST['stripeToken']
        price = float(request.POST['price'])
        termId = request.POST['termId']
        quantity = int(request.POST['quantity'])
        email = request.POST['email']
        firstname = request.POST['firstName']
        lastname = request.POST['lastName']
        institute = request.POST['institute']
        street = request.POST['street']
        city = request.POST['city']
        state = request.POST['state']
        country = request.POST['country']
        zip = request.POST['zip']
        hostname = request.META.get("HTTP_ORIGIN")
        redirect = request.POST['redirect']
        other = request.POST['other'] #PW-248. Let it be in two places - in descriptionPartnerDuration and in email body
        termObj = SubscriptionTerm.objects.get(subscriptionTermId=termId)
        subDescription = termObj.category + " | "  + termObj.description
        partnerName = termObj.partnerId.name
        chargeDescription = '%s %s subscription; other info: %s; name: %s %s'%(partnerName,subDescription,other,firstname,lastname)
        domain = request.POST['domain']

        message = PaymentControl.chargeForCIPRES(partyId, userIdentifier, stripe_api_secret_test_key, token, price, partnerName, chargeDescription, termId, quantity, email, firstname, lastname, institute, street, city, state, country, zip, hostname, redirect, other, domain)
        #PW-120 vet
        status = 200
        if 'message' in message:
            status = 400
        return HttpResponse(json.dumps(message), content_type="application/json", status=status)

# CIPRES-107
class ApplyDiscount(APIView):
    """
    Apply discount code to the provided price with enhancements:
    - Handle multiple discount codes with different discount rates
    - Ensure the original price is valid (greater than 0)
    """
    requireApiKey = False
    DISCOUNT_CODES = {
        'CIPRES10': 0.9,  # 20% discount
    }
    def post(self, request):
        data = request.data
        original_price = float(data.get('price', 0))
        discount_code = data.get('discountCode', '').upper()  # Normalize the code to uppercase
        # Check if a valid price is provided
        if original_price <= 0:
            return Response({'success': False, 'error': 'Invalid original price.'}, status=status.HTTP_400_BAD_REQUEST)
        # Validate the discount code
        discount_factor = self.DISCOUNT_CODES.get(discount_code)
        if discount_factor:
            discounted_price = original_price * discount_factor
            success = True
            response_data = {'success': success, 'newSubtotal': discounted_price}
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'error': 'Invalid discount code. Please make sure you are using a correct discount code.'}, status=status.HTTP_200_OK)


# /usage-tier/terms
# CYV-10: End point for querying usage tiers for CyVerse
# params: partnerId
# returns: a list of UsageTierTerm records in JSON format
class UsageTierTermCRUD(GenericCRUDView):
    requireApiKey = False
    queryset = UsageTierTerm.objects.all()
    serializer_class = UsageTierTermSerializer

    def post(self, request):
        return Response({'msg':'cannot create'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        return Response({'msg':'cannot update'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        return Response({'msg':'cannot delete'}, status=status.HTTP_400_BAD_REQUEST)

# /usage-tier/addons
# CYV-42: End point for querying add on options for CyVerse
# params: partnerId
# returns: a list of UsageAddonOptions records in JSON format
class UsageAddonOptionsCRUD(GenericCRUDView):
    requireApiKey = False
    queryset = UsageAddonOption.objects.all()
    serializer_class = UsageAddonOptionSerializer

    def post(self, request):
        return Response({'msg':'cannot create'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        return Response({'msg':'cannot update'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        return Response({'msg':'cannot delete'}, status=status.HTTP_400_BAD_REQUEST)

# /active-usage-tier-purchase
# CYV-5: End point for querying a user's usage tier purchased which is still active (endDate > now)
# params: username, partnerId
# returns: a list of UsageTier records in JSON format
class ActiveUsageTierPurchase(generics.GenericAPIView):
    requireApiKey = False
    def get(self,request):
        params = request.GET
        # not checking param existence since it is only used by Phoenix's resources
        partnerId = params['partnerId']
        username = params['username']
        try:
            credentialObj = Credential.getByUsernameAndPartner(username, partnerId)
            partyId = credentialObj.partyId.partyId
            activePurchases = UsageTierPurchase.getActiveByIdAndPartner(partyId, partnerId)
            if activePurchases:
                serializer = UsageTierPurchaseSerializer(activePurchases[0])
                return HttpResponse(json.dumps(dict(serializer.data)), content_type="application/json")
        except Credential.DoesNotExist:
            pass
        except Credential.MultipleObjectsReturned:
            pass
        return HttpResponse(json.dumps(None), content_type="application/json")

# /cyverse-subscription
# CYV-42: End point for querying a user's subscription tier and add on options purchased 
# by sending request to the CyVerse API
# params: username
# returns: a JSON string with subscription tier, subscription UUID and endDate
class CyVerseSubscriptionTier(generics.GenericAPIView):
    requireApiKey = False
    def get(self,request):
        params = request.GET
        # not checking param existence since it is only used by Phoenix's resources
        username = params['username']
        try:
            client = CyVerseClient()
            subscription = client.getSubscriptionTier(username)
            addOns = client.getAddonPurchases(subscription['uuid'])
            return HttpResponse(json.dumps({'subscription': subscription, 'addons': addOns}), content_type="application/json")
        except Exception as error:
            return HttpResponse(json.dumps(error), content_type="application/json", status=400)

# /cyverse-subscription-v2
# Endpoint for querying a user's latest subscription tier and add on options purchased
# from the updated subscription API that returns multiple subscriptions
# params: username
# returns: a JSON string with subscription tier, subscription UUID and endDate from the latest subscription
class CyVerseSubscriptionTierV2(generics.GenericAPIView):
    requireApiKey = False
    
    def get(self, request):
        params = request.GET
        username = params.get('username')
        
        if not username:
            return HttpResponse(
                json.dumps({'error': 'Username parameter is required'}),
                content_type="application/json",
                status=400
            )
            
        try:
            client = CyVerseClient()
            subscription = client.getLatestSubscriptionTier(username)
            addOns = client.getAddonPurchases(subscription['uuid'])
            
            return HttpResponse(
                json.dumps({
                    'subscription': subscription,
                    'addons': addOns
                }),
                content_type="application/json"
            )
            
        except Exception as error:
            error_message = str(error)
            return HttpResponse(
                json.dumps({'error': error_message}),
                content_type="application/json",
                status=400
            )
        
# /payments/usage-tier
# CYV-17: End point for posting payment for CyVerse
class UsageTierPayment(APIView):
    requireApiKey = False

    def post(self, request):
        stripe_api_key = settings.STRIPE_PRIVATE_KEY
        username = request.POST['username']
        token = request.POST['stripeToken']
        price = float(request.POST['price'])
        email = request.POST['email']
        firstname = request.POST['firstName']
        lastname = request.POST['lastName']
        institute = request.POST['institute']
        street = request.POST['street']
        city = request.POST['city']
        state = request.POST['state']
        country = request.POST['country']
        zip = request.POST['zip']
        hostname = request.META.get("HTTP_ORIGIN")
        redirect = request.POST['redirect']
        cardLast4 = request.POST['cardLast4']
        other = request.POST['other'] #PW-248. Let it be in two places - in descriptionPartnerDuration and in email body
        domain = request.POST['domain']
        subscription = json.loads(request.POST['subscription'])

        message = PaymentControl.chargeForCyVerse(stripe_api_key, token, price, subscription, username, email, firstname, lastname, institute, street, city, state, country, zip, hostname, redirect, cardLast4, other, domain)
        status = 200
        if 'message' in message:
            status = 400
        return HttpResponse(json.dumps(message), content_type="application/json", status=status)
