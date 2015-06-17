#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from partner.models import Partner, PartnerPattern, SubscriptionTerm
from rest_framework import serializers

class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = ('partnerId','name')

class PartnerPatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerPattern
        fields = ('partnerPatternId', 'partnerId','sourceUri', 'targetUri')

class SubscriptionTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionTerm
        fields = ('subscriptionTermId','period','price','groupDiscountPercentage','partnerId')
