#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.


from subscription.models import Subscription, SubscriptionTransaction
from rest_framework import serializers
from partner.models import Partner

class SubscriptionSerializer(serializers.ModelSerializer):
    def validate_partyId(self, value):
#        Partner.validatePartnerId(self, value.partnerId.partnerId)
        return value
    class Meta:
        model = Subscription
        fields = ('subscriptionId', 'partyId', 'partnerId', 'startDate', 'endDate')

class SubscriptionTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionTransaction
        fields = ('subscriptionTransactionId','subscriptionId','transactionDate','startDate','endDate','transactionType')
