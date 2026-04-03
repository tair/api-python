#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.


from subscription.models import *
from rest_framework import serializers
from partner.models import Partner, BucketType
from django.utils import timezone
from datetime import timedelta

class UserTrackPagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTrackPages
        fields = ('userTrackPagesId', 'uri', 'timestamp', 'partyId')

class UserBucketUsageSerializer(serializers.ModelSerializer):
    first_annual_purchase_date = serializers.SerializerMethodField()
    discountPercentage = serializers.SerializerMethodField()

    def _get_orcid_id_for_usage(self, usage):
        from authentication.models import Credential, OrcidCredentials

        credential = Credential.objects.filter(partyId=usage.partyId, partnerId='tair').first()
        if not credential:
            return None

        orcid_cred = OrcidCredentials.objects.filter(credential=credential).exclude(orcid_id__isnull=True).exclude(orcid_id='').first()
        if not orcid_cred or not orcid_cred.orcid_id:
            return None

        return orcid_cred.orcid_id

    def _get_first_purchase_in_annual_window(self, orcid_id, transaction_type=None):
        from subscription.controls import SubscriptionControl
        return SubscriptionControl.get_first_recent_bucket_purchase(orcid_id, bucket_type_id=10, transaction_type=transaction_type)

    def get_first_annual_purchase_date(self, usage):
        # Date when the current annual-window discount cycle started.
        # Only consider actual purchases, not activation code redemptions.
        orcid_id = self._get_orcid_id_for_usage(usage)
        first_purchase = self._get_first_purchase_in_annual_window(orcid_id, transaction_type='create_bucket')

        if not first_purchase:
            return None

        return first_purchase.transaction_date

    def get_discountPercentage(self, usage):
        # Mirror bucket pricing behavior for 300-unit annual discount.
        # If ORCID is missing OR there is a purchase in the last 365 days,
        # discount is 0. Otherwise return configured bucket discount.
        try:
            base_discount = BucketType.objects.get(bucketTypeId=10).discountPercentage
        except BucketType.DoesNotExist:
            return 0

        orcid_id = self._get_orcid_id_for_usage(usage)
        if not orcid_id:
            return 0

        first_purchase = self._get_first_purchase_in_annual_window(orcid_id)
        if first_purchase:
            return 0

        return base_discount

    class Meta:
        model = UserBucketUsage
        fields = (
            'user_usage_id',
            'partyId',
            'partner_id',
            'total_units',
            'remaining_units',
            'expiry_date',
            'free_expiry_date',
            'first_annual_purchase_date',
            'discountPercentage'
        )

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