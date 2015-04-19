#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from subscription.models import Party, Payment, Subscription, SubscriptionIpRange, SubscriptionTerm
from rest_framework import serializers

class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ('partyId','partyType')

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('paymentId','partyId')

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('partyId', 'subscriptionTermId', 'startDate', 'endDate')

class SubscriptionIpRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionIpRange
        fields = ('subscriptionIpRangeId','start','end','partyId')

class SubscriptionTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionTerm
        fields = ('subscriptionTermId','period','price','groupDiscountPercentage','autoRenew')
