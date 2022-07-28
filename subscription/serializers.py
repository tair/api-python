#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.


from subscription.models import Subscription, SubscriptionTransaction, ActivationCode, SubscriptionRequest, UsageUnitPurchase, UsageTierTerm, UsageTierPurchase
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

class UsageUnitPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageUnitPurchase
        fields = ('purchaseId', 'partyId', 'partnerId', 'quantity', 'purchaseDate', 'transactionId', 'syncedToPartner')

class UsageTierTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageTierTerm
        fields = ('tierId', 'partnerId', 'name', 'label', 'price', 'isAcademic', 'durationInDays')

class UsageTierPurchaseSerializer(serializers.ModelSerializer):
    tierName = serializers.SerializerMethodField('get_term_name')
    tierLabel = serializers.SerializerMethodField('get_term_label')

    def get_term_name(self, purchase):
        return purchase.tierId.name

    def get_term_label(self, purchase)
        return purchase.tierId.label

    class Meta:
        model = UsageTierPurchase
        fields = ('purchaseId', 'partyId', 'partnerId', 'tierId', 'tierName', 'tierLabel', 'purchaseDate', 'expirationDate', 'transactionId', 'syncedToPartner')