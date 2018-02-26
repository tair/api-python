#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.


from party.models import Party, IpRange, Country
from rest_framework import serializers

class PartySerializer(serializers.ModelSerializer):
    ipRangeCount = serializers.SerializerMethodField() # Used SerializerMethodField to add a customized field which returns number of ip ranges
    class Meta:
        model = Party
        fields = ('partyId','partyType', 'name', 'country', 'display', 'consortiums', 'label', 'ipRangeCount')
    def get_ipRangeCount(self, obj): # Method for SerializerMethodField
        return obj.iprange_set.count()

class IpRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IpRange
        fields = ('ipRangeId','start','end','partyId', 'label')

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('countryId','name')
