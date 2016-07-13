#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.
from authentication.models import Credential
from rest_framework import serializers

class CredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credential
        fields = ('username', 'firstName', 'lastName', 'password', 'email', 'institution', 'partyId', 'partnerId', 'userIdentifier')#PW-161

class CredentialSerializerNoPassword(serializers.ModelSerializer):
    class Meta:
        model = Credential
        fields = ('username', 'firstName', 'lastName', 'email', 'institution', 'partyId', 'partnerId', 'userIdentifier')#PW-161

