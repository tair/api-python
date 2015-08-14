#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.http import HttpResponse

from subscription.controls import PaymentControl, SubscriptionControl
from subscription.models import Subscription, SubscriptionTransaction, ActivationCode
from subscription.serializers import SubscriptionSerializer, SubscriptionTransactionSerializer, ActivationCodeSerializer

from partner.models import Partner, SubscriptionTerm
from party.models import Party
from authentication.models import User

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from common.views import GenericCRUDView

from django.shortcuts import render
import stripe
import json

import datetime

from django.conf import settings

from django.core.mail import send_mail

# top level: /subscriptions/

# Basic CRUD operation for Subscriptions, and SubscriptionTransactions

# /
class SubscriptionCRUD(GenericCRUDView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    requireApiKey = False

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
	
        description = "Test charge"
        message = PaymentControl.tryCharge(stripe_api_secret_test_key, token, price, description, termId, quantity, email, firstname, lastname, institute, street, city, state, country, zip, hostname)
        return HttpResponse(json.dumps(message), content_type="application/json")

# /institutions/
class InstitutionSubscription(APIView):
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

        from_email = "steve@getexp.com"
        recipient_list = ["steve@getexp.com", "azeem@getexp.com"]
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
        return HttpResponse(json.dumps({'message':'success'}), content_type="application/json")

# /commercials/
class CommercialSubscription(APIView):
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

        from_email = "steve@getexp.com"
        recipient_list = ["steve@getexp.com", "azeem@getexp.com"]
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
        return HttpResponse(json.dumps({'message':'success'}), content_type="application/json")

# /<userIdentifier>/expdatebyuseridentifier/
class EndDate(generics.GenericAPIView):
    def get(self, request):
        partnerId=request.GET.get("partnerId")
        userIdentifier=request.GET.get("userIdentifier")
        expDate = ""
        subscribed = False
        if User.objects.filter(userIdentifier=userIdentifier).filter(partnerId=partnerId).exists():
            partyId = User.objects.filter(userIdentifier=userIdentifier)[0].partyId.partyId
            sub = Subscription.getActiveById(partyId, partnerId)
            if len(sub)>0:
                expDate = SubscriptionSerializer(sub[0]).data['endDate']
                subscribed = True
        return HttpResponse(json.dumps({'expDate':expDate, 'subscribed':subscribed}), content_type="application/json")
