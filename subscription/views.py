#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.http import HttpResponse

from subscription.controls import PaymentControl
from subscription.models import Subscription, SubscriptionTransaction
from subscription.serializers import SubscriptionSerializer, SubscriptionTransactionSerializer

from partner.models import Partner, SubscriptionTerm

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from common.views import GenericCRUDView

from django.shortcuts import render
import stripe
import json

import datetime
# top level: /subscriptions/

# Basic CRUD operation for Subscriptions, and SubscriptionTransactions

# /
class SubscriptionCRUD(GenericCRUDView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    # overrides default POST to create a subscription transaction
    def post(self, request):
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

#------------------- End of Basic CRUD operations --------------


# Specific queries

# /active/
class SubscriptionsActive(APIView):
    def get(self, request, format=None):
        partyId = request.GET.get('partyId')
        ip = request.GET.get('ip')
        isActive = False
        if not partyId == None and partyId.isdigit():
            objList = Subscription.getActiveById(partyId)
            isActive = isActive or len(objList) > 0
        if not ip == None:
            objList = Subscription.getActiveByIp(ip)
            isActive = isActive or len(objList) > 0

        # TODO add in security check to filter objList

        return HttpResponse(json.dumps({'active':isActive}), content_type="application/json")


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
    def get(self, request):
        message = {}
        if (not PaymentControl.isValidRequest(request, message)):
            return HttpResponse(message['message'], 400)
        termId=request.GET.get('termId')
        partyId=request.GET.get('partyId')
        #Currently assumes that subscription objects in database stores price in cents
        #TODO: Handle more human readable price
        message['price'] = int(SubscriptionTerm.objects.get(subscriptionTermId=termId).price)
        message['partyId'] = partyId
        message['termId'] = termId
        return render(request, "subscription/paymentIndex.html", message)

    def post(self, request):
        stripe_api_secret_test_key = PaymentControl.stripe_api_secret_test_key
        stripe.api_key = stripe_api_secret_test_key
        token = request.POST['stripeToken']
        price = int(request.POST['price'])
        partyId = request.POST['partyId']
        termId = request.POST['termId']
        description = "Test charge"
        status, message = PaymentControl.tryCharge(stripe_api_secret_test_key, token, price, description, partyId, termId)
        if status:
            return HttpResponse(message['message'], 201)
        return render(request, "subscription/paymentIndex.html", message)
