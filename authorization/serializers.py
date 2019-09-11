#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from .models import AccessType, AccessRule, UriPattern
from rest_framework import serializers

class AccessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessType
        fields = ('accessTypeId','name')

class AccessRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessRule
        fields = ('accessRuleId', 'patternId', 'accessTypeId', 'partnerId')

class UriPatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = UriPattern
        fields = ('patternId', 'pattern', 'redirectUri')
