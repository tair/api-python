#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.


from party.models import Party, IpRange
from rest_framework import serializers

class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ('partyId','partyType', 'name', 'country', 'display', 'consortiums', 'label')

class IpRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IpRange
        fields = ('ipRangeId','start','end','partyId', 'label')
