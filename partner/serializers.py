#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from partner.models import Partner, PartnerPattern, SubscriptionTerm, BucketType, SubscriptionDescription, SubscriptionDescriptionItem
from rest_framework import serializers

class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = ('partnerId','name','logoUri','homeUri','termOfServiceUri', 'description','loginUri', 'defaultLoginRedirect', 'uiUri', 'uiMeterUri',
                  'registerUri', 'subscriptionListDesc', 'registerText', 'forgotUserNameEmailTo', 
                  'forgotUserNameEmailSubject', 'forgotUserNameEmailBody', 'forgotUserNameText', 
                  'activationEmailInstructionText', 'loginUserNameFieldPrompt', 'loginPasswordFieldPrompt', 
                  'resetPasswordEmailBody', 'loginRedirectErrorText', 'guideUri')

class BucketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BucketType
        fields =  ('bucketTypeId', 'units', 'price', 'partnerId', 'description', 'discountPercentage')

class PartnerPatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerPattern
        fields = ('partnerPatternId', 'partnerId','sourceUri', 'targetUri')

class SubscriptionTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionTerm
        fields = ('subscriptionTermId','period','price','groupDiscountPercentage','partnerId','description', 'category')

class SubscriptionDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionDescription
        fields = ('subscriptionDescriptionId', 'header', 'partnerId', 'descriptionType')

class SubscriptionDescriptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionDescriptionItem
        fields = ('subscriptionDescriptionItemId', 'subscriptionDescriptionId', 'text')
