#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from .models import ApiKey
from rest_framework import serializers

class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKey
        fields = ('apiKeyId', 'apiKey')
