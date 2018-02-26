#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.


from party.models import Party, IpRange, Country
from rest_framework import serializers

class PartySerializer(serializers.ModelSerializer):
    hasIpRange = serializers.SerializerMethodField() # Used SerializerMethodField to add a customized field which returns a boolean
    class Meta:
        model = Party
        fields = ('partyId','partyType', 'name', 'country', 'display', 'consortiums', 'label', 'hasIpRange')
    def get_hasIpRange(self, obj): # Method for SerializerMethodField
        return True if obj.iprange_set.count() else False

class IpRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IpRange
        fields = ('ipRangeId','start','end','partyId', 'label')

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('countryId','name')
