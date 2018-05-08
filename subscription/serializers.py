#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.


from subscription.models import Subscription, SubscriptionTransaction, ActivationCode, SubscriptionRequest
from rest_framework import serializers
from partner.models import Partner

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('subscriptionId', 'partyId', 'partnerId', 'startDate', 'endDate', 'consortiumStartDate', 'consortiumEndDate', 'consortiumId')

class SubscriptionTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionTransaction
        fields = ('subscriptionTransactionId','subscriptionId','transactionDate','startDate','endDate','transactionType')

class ActivationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivationCode
        fields = ('activationCodeId', 'activationCode', 'partnerId', 'partyId', 'period', 'purchaseDate', 'deleteMarker')

class SubscriptionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionRequest
        fields = ('subscriptionRequestId','requestDate','firstName','lastName','email','institution','librarianName','librarianEmail','comments','partnerId','requestType')
