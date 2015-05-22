#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.
from authentication.models import UsernamePartyAffiliation
from rest_framework import serializers

class usernamePartyAffiliationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsernamePartyAffiliation
        fields = ('username', 'password', 'email', 'organization', 'partyId')


class usernamePartyAffiliationSerializerNoPassword(serializers.ModelSerializer):
    class Meta:
        model = UsernamePartyAffiliation
        fields = ('username', 'email', 'organization', 'partyId')

