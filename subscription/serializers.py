#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from subscription.models import Party, SubscriptionState, SubscriptionIpRange, SubscriptionTerm
from rest_framework import serializers
from partner.models import Partner

class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ('partyId','partyType')

class SubscriptionStateSerializer(serializers.ModelSerializer):
    def validate_partyId(self, value):
#        Partner.validatePartnerId(self, value.partnerId.partnerId)
        return value
    class Meta:
        model = SubscriptionState
        fields = ('subscriptionStateId', 'partyId', 'partnerId', 'startDate', 'endDate')

class SubscriptionIpRangeSerializer(serializers.ModelSerializer):
    def validate_partyId(self, value):
#        Partner.validatePartnerId(self, value.partyId.partnerId.partnerId)
        return value
    class Meta:
        model = SubscriptionIpRange
        fields = ('subscriptionIpRangeId','start','end','partyId')

class SubscriptionTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionTerm
        fields = ('subscriptionTermId','period','price','groupDiscountPercentage','autoRenew', 'partnerId')
