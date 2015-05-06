#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from partner.models import Partner
from rest_framework import serializers

class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = ('partnerId','name','accessKey')
