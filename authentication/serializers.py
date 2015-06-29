#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.
from authentication.models import User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'institution', 'partyId', 'partnerId', 'userIdentifier')

class UserSerializerNoPassword(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'institution', 'partyId', 'partnerId', 'userIdentifier')

