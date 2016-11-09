#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.http import HttpResponse, StreamingHttpResponse

from subscription.controls import PaymentControl, SubscriptionControl
from subscription.models import Subscription, SubscriptionTransaction, ActivationCode, SubscriptionRequest
from subscription.serializers import SubscriptionSerializer, SubscriptionTransactionSerializer, ActivationCodeSerializer, SubscriptionRequestSerializer

from partner.models import Partner, SubscriptionTerm
from party.models import Party
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

import logging

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
        elif all(param in params for param in ['partnerId', 'ipAddress', 'userIdentifier']):
            partnerId = params['partnerId']
            ipAddress = params['ipAddress']
            userIdentifier = params['userIdentifier']
            idSub = None #Pw-418
            subList = [] #Pw-418
            ipSub = Subscription.getByIp(ipAddress).filter(partnerId=partnerId)
            if Credential.objects.filter(userIdentifier=userIdentifier).filter(partnerId=partnerId).exists():
                partyId = Credential.objects.filter(partnerId=partnerId).filter(userIdentifier=userIdentifier)[0].partyId.partyId
                idSub = Subscription.getById(partyId)
            if (idSub):
                subList = SubscriptionSerializer(ipSub, many=True).data+SubscriptionSerializer(idSub, many=True).data
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
                transaction = SubscriptionTransaction.createFromSubscription(subscription, 'create')
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
        vat = request.POST['vat'] #PW-248. Let it be in two places - in descriptionPartnerDuration and in email body
        #PW-204 requirement: "TAIR 1-year subscription" would suffice.
        descriptionDuration = SubscriptionTerm.objects.get(subscriptionTermId=termId).description
        partnerName = SubscriptionTerm.objects.get(subscriptionTermId=termId).partnerId.name
        descriptionPartnerDuration = partnerName+" "+descriptionDuration +" subscription"+" vat:"+vat
        domain = request.POST['domain']

        message = PaymentControl.tryCharge(stripe_api_secret_test_key, token, price, descriptionPartnerDuration, termId, quantity, email, firstname, lastname, institute, street, city, state, country, zip, hostname, redirect, vat, domain)
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
#        logging.error("------Sending institution subscription email------")
#        logging.error("%s" % subject)
#        logging.error("%s" % message)

        from_email = "info@phoenixbioinformatics.org"
        recipient_list = ["yarik@arabidopsis.org", "info@phoenixbioinformatics.org"]
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

        message += "\nSubmitter's public IP Address: " + getRemoteIpAddress(request)

#        logging.basicConfig(filename="/home/ec2-user/logs/debug.log",
#                            format='%(asctime)s %(message)s'
#        )
#        logging.error("------Sending commercial subscription email------")
#        logging.error("%s" % subject)
#        logging.error("%s" % message)

        from_email = "info@phoenixbioinformatics.org"
        recipient_list = ["yarik@arabidopsis.org", "info@phoenixbioinformatics.org"]
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
#        logging.error("------Done sending commercial email------")
        return HttpResponse(json.dumps({'message':'success'}), content_type="application/json")

# /enddate
# Among all the subscriptions to a given partner, looks for the effective subscription that either covers the given IP address or belongs to the given party.
# Upon success, returns the expiration date of the found subscription and 'subscribed' status as True; otherwise, the returned expiration date is null and status is False.
class EndDate(generics.GenericAPIView):
    requireApiKey = False
    def get(self, request):
        partnerId=request.GET.get("partnerId")
        ipAddress=request.GET.get("ipAddress")
        userIdentifier=request.GET.get("userIdentifier")
        expDate = ""
        subscribed = False
        ipSub = Subscription.getActiveByIp(ipAddress, partnerId)
        idSub = None #Pw-418
        subList = [] #Pw-418
        if Credential.objects.filter(userIdentifier=userIdentifier).filter(partnerId=partnerId).exists():
            partyId = Credential.objects.filter(partnerId=partnerId).filter(userIdentifier=userIdentifier)[0].partyId.partyId
            idSub = Subscription.getActiveById(partyId, partnerId)
        if (idSub):
            subList = SubscriptionSerializer(ipSub, many=True).data+SubscriptionSerializer(idSub, many=True).data
        if subList != []:
            subscribed = True
            expDate = max(sub['endDate'] for sub in subList)
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
        from_email = "info@phoenixbioinformatics.org"
        recipient_list = ["qianli1987@phoenixbioinformatics.org"]
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
        from_email = "info@phoenixbioinformatics.org"
        recipient_list = ["qianli1987@phoenixbioinformatics.org"]
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
        return HttpResponse(json.dumps({'message':'success'}), content_type="application/json")

# /edit/
class SubscriptionEdit(generics.GenericAPIView):#TODO: act only as admin
    requireApiKey = False
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def put(self, request):
        if not isPhoenix(request):
           return HttpResponse(status=400)
        # partnerId = request.GET.get('partnerId')
        # subscription = Subscription.objects.all().filter(partnerId=partnerId)[0]
        if 'subscriptionId' in request.GET:
            subscriptionId = request.GET.get('subscriptionId')
            subscription = Subscription.objects.all().get(subscriptionId=subscriptionId)
        else:
            return Response({'error':'subscriptionId required'})
        serializer = SubscriptionSerializer(subscription, data=request.data)
        if serializer.is_valid():
            subscription = serializer.save()
            returnData = serializer.data
            return Response(returnData)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# /institutions1/
class InstitutionSubscription1(APIView):
    requireApiKey = False
    def post (self, request):
        data = request.data
        to_email = data.get('email')
        subject = "Phoenix Bioinformatics Password Reset"

        length = 8
        chars = string.ascii_letters + string.digits + '!@#$%^&*()'
        temp_password = ''.join(random.choice(chars) for i in range(length))
        data['password'] = hashlib.sha1(temp_password).hexdigest()

        if Credential.objects.all().filter(email=to_email,partnerId='phoenix'):
            credential = Credential.objects.all().filter(email=to_email,partnerId='phoenix')[0]
            serializer = CredentialSerializer(credential, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
            username = serializer.data['username']

            message = 'Username: '+username + '(' + to_email + ')\n'
            message += "Your temporary password is: " + temp_password + '\n'
            message += "Please log on to your account and change your password."

            from_email = "info@phoenixbioinformatics.org"
            recipient_list = []
            recipient_list.append(to_email)
            send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)

            return HttpResponse(json.dumps({'message':'success'}), content_type="application/json")
        else:
            return Response({'error':'Cannot find registered email address.'},status=status.HTTP_400_BAD_REQUEST)


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
        for sub in subList:
            if Party.objects.filter(partyId = sub['partyId']).exists():
                party = PartySerializer(Party.objects.get(partyId = sub['partyId'])).data
                sub['partyType'] = party['partyType']
                sub['name'] = party['name']
        return HttpResponse(json.dumps(subList), content_type="application/json")


