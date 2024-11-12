#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.


from subscription.models import *
from rest_framework import serializers
from partner.models import Partner

class UserTrackPagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTrackPages
        fields = ('userTrackPagesId', 'uri', 'timestamp', 'partyId')

class UserBucketUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBucketUsage
        fields = ('user_usage_id', 'partyId', 'partner_id', 'total_units', 'remaining_units', 'expiry_date', 'free_expiry_date')

class BucketTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BucketTransaction
        fields = '__all__'
        
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

    def get_term_label(self, purchase):
        return purchase.tierId.label

    class Meta:
        model = UsageTierPurchase
        fields = ('purchaseId', 'partyId', 'partnerId', 'tierId', 'tierName', 'tierLabel', 'purchaseDate', 'expirationDate', 'transactionId', 'syncedToPartner')

class UsageAddonPricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageAddonPricing
        fields = ('price', 'priority', 'threshold')

class UsageAddonOptionSerializer(serializers.ModelSerializer):
    pricing = UsageAddonPricingSerializer(many=True, read_only=True)

    class Meta:
        model = UsageAddonOption
        fields = ('optionId', 'partnerId', 'partnerUUID', 'quantity', 'unit', 'name', 'description', 'durationInDays', 'proportional', 'pricing')