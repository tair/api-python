#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.





from metering.models import IpAddressCount, LimitValue
from rest_framework import serializers

class IpAddressCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = IpAddressCount
        fields = ('id', 'ip', 'count', 'partnerId')

class LimitValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = LimitValue
        fields = ('limitId', 'val', 'partnerId', 'pattern')
