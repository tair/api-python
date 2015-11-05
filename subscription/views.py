#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.http import HttpResponse

from subscription.controls import PaymentControl, SubscriptionControl
from subscription.models import Subscription, SubscriptionTransaction, ActivationCode
from subscription.serializers import SubscriptionSerializer, SubscriptionTransactionSerializer, ActivationCodeSerializer

from partner.models import Partner, SubscriptionTerm
from party.models import Party
from authentication.models import Credential

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from common.views import GenericCRUDView
from common.permissions import isPhoenix

from django.shortcuts import render
import stripe
import json

import datetime

from django.conf import settings

from django.core.mail import send_mail

import logging

# top level: /subscriptions/

# Basic CRUD operation for Subscriptions, and SubscriptionTransactions

# /
class SubscriptionCRUD(GenericCRUDView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    requireApiKey = False

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

            partyId = request.data['partyId']
            partnerId = activationCodeObj.partnerId.partnerId
            period = activationCodeObj.period
            # retrive and update existing subscription, or creat a new one if partner/party does
            # not already have one.
            (subscription, transactionType, transactionStartDate, transactionEndDate) = SubscriptionControl.createOrUpdateSubscription(partyId, partnerId, period)

            subscription.save()
            transaction = SubscriptionTransaction.createFromSubscription(subscription, transactionType, transactionStartDate, transactionEndDate)

            # set activationCodeObj to be used.
            partyObj = Party.objects.get(partyId=partyId)
            activationCodeObj.partyId = partyObj
            activationCodeObj.save()
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
                transaction = SubscriptionTransaction.createFromSubscription(subscription, 'Initial')
                returnData = serializer.data
                returnData['subscriptionTransactionId']=transaction.subscriptionTransactionId
                return Response(returnData, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# /transactions/
class SubscriptionTransactionCRUD(GenericCRUDView):
    queryset = SubscriptionTransaction.objects.all()
    serializer_class = SubscriptionTransactionSerializer

# /activationCodes/
class ActivationCodeCRUD(GenericCRUDView):
    queryset = ActivationCode.objects.all()
    serializer_class = ActivationCodeSerializer

#------------------- End of Basic CRUD operations --------------


# Specific queries

# /<pk>/renewal/
class SubscriptionRenewal(generics.GenericAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def put(self, request, pk):
        subscription = Subscription.objects.get(subscriptionId=pk)
        serializer = SubscriptionSerializer(subscription, data=request.data)
        if serializer.is_valid():
            subscription = serializer.save()
            transaction = SubscriptionTransaction.createFromSubscription(subscription, 'Renewal')
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
	
        description = "Test charge"
        message = PaymentControl.tryCharge(stripe_api_secret_test_key, token, price, description, termId, quantity, email, firstname, lastname, institute, street, city, state, country, zip, hostname, redirect)
        return HttpResponse(json.dumps(message), content_type="application/json")

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

#        logging.basicConfig(filename="/home/ec2-user/logs/debug.log",
#                            format='%(asctime)s %(message)s'
#        )
#        logging.error("------Sending institution subscription email------")
#        logging.error("%s" % subject)
#        logging.error("%s" % message)
        #from_email = "steve@getexp.com"
        from_email = "info@phoenixbioinformatics.org"
        recipient_list = ["steve@getexp.com", "info@phoenixbioinformatics.org"]
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
#        logging.error("------Done sending institution subscription email------")

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

        if data.get('individualLicense'):
            message += "Individual Licenses\n"
        if data.get('commercialLicense'):
            message += "Commercial Licenses\n"

#        logging.basicConfig(filename="/home/ec2-user/logs/debug.log",
#                            format='%(asctime)s %(message)s'
#        )
#        logging.error("------Sending commercial subscription email------")
#        logging.error("%s" % subject)
#        logging.error("%s" % message)

        from_email = "info@phoenixbioinformatics.org"
        recipient_list = ["steve@getexp.com", "info@phoenixbioinformatics.org"]
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
#        logging.error("------Done sending commercial email------")
        return HttpResponse(json.dumps({'message':'success'}), content_type="application/json")

# /<userIdentifier>/expdatebyuseridentifier/
class EndDate(generics.GenericAPIView):
    def get(self, request):
        partnerId=request.GET.get("partnerId")
        userIdentifier=request.GET.get("userIdentifier")
        expDate = ""
        subscribed = False
        if Credential.objects.filter(userIdentifier=userIdentifier).filter(partnerId=partnerId).exists():
            partyId = Credential.objects.filter(userIdentifier=userIdentifier)[0].partyId.partyId
            sub = Subscription.getActiveById(partyId, partnerId)
            if len(sub)>0:
                expDate = SubscriptionSerializer(sub[0]).data['endDate']
                subscribed = True
        return HttpResponse(json.dumps({'expDate':expDate, 'subscribed':subscribed}), content_type="application/json")

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

# /renew/
class RenewSubscription(generics.GenericAPIView):
    requireApiKey = False
    def post(self, request):
        if not isPhoenix(request):
            return HttpResponse(status=400)
        data = request.data
        dataTuple = (
            data.get('name'),
            data.get('email'),
            data.get('institution'),
	    data.get('comments'),
        )
        subject = "%s Subscription Renewal Request For %s" % (data.get('partnerName'), data.get('institution'))
        message = "\n" \
                  "\n" \
                  "Please contact me about a subscription renewal. My information is below.\n" \
                  "Name: %s\n" \
                  "Email: %s \n" \
                  "Institution Name: %s \n" \
		  "Comments: %s \n" \
                  "\n" \
                  % dataTuple
        from_email = "info@phoenixbioinformatics.org"
        recipient_list = ["info@phoenixbioinformatics.org"]
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
        return HttpResponse(json.dumps({'message':'success'}), content_type="application/json")

# /request/
class RequestSubscription(generics.GenericAPIView):
    requireApiKey = False
    def post(self, request):
        if not isPhoenix(request):
            return HttpResponse(status=400)
        data = request.data
        dataTuple = (
            data.get('name'),
            data.get('email'),
            data.get('institution'),
	    data.get('comments'),
        )
        subject = "%s Subscription Request For %s" % (data.get('partnerName'), data.get('institution'))
        message = "\n" \
                  "\n" \
                  "Please contact me about a subscription renewal. My information is below.\n" \
                  "Name: %s\n" \
                  "Email: %s \n" \
                  "Institution Name: %s \n" \
		  "Comments: %s \n" \
                  "\n" \
                  % dataTuple
        from_email = "info@phoenixbioinformatics.org"
        recipient_list = ["info@phoenixbioinformatics.org"]
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
        return HttpResponse(json.dumps({'message':'success'}), content_type="application/json")

# /<pk>/edit/
class SubscriptionEdit(generics.GenericAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def put(self, request, pk):
        subscription = Subscription.objects.get(subscriptionId=pk)
        serializer = SubscriptionSerializer(subscription, data=request.data)
        if serializer.is_valid():
            subscription = serializer.save()
            transaction = SubscriptionTransaction.createFromSubscription(subscription, 'Renewal')
            returnData = serializer.data
            returnData['subscriptionTransactionId']=transaction.subscriptionTransactionId
            return Response(returnData)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# /getall/
class GetAllSubscription(generics.GenericAPIView):

    def get(self, request):
        subscriptionList = Subscription.objects.all()

        if request.GET.get('authority')=='admin': #TODO: return only the user is admin user
            return Response(subscriptionList)
        return Response(status=status.HTTP_400_BAD_REQUEST)