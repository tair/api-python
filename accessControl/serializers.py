#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from models import AccessType, AccessRule, Pattern
from rest_framework import serializers

class AccessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessType
        fields = ('accessTypeId','name')

class AccessRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessRule
        fields = ('accessRuleId', 'patternId', 'accessTypeId')

class PatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pattern
        fields = ('patternId', 'pattern')
