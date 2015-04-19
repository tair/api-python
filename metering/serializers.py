#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.





from metering.models import ipAddr, limits
from rest_framework import serializers

class ipSerializer(serializers.ModelSerializer):
    class Meta:
        model = ipAddr
        fields = ('ip', 'count')

class limitSerializer(serializers.ModelSerializer):
    class Meta:
        model = limits
        fields = ('name', 'val')
