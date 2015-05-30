#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.


from loggingapp.models import Sessions2, PageViews2
from rest_framework import serializers

class sessionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sessions2
        fields = ('sessionId', 'sessionStartDateTime', 'sessionEndDateTime', 'sessionPartnerId')

class pageViewsSerializer(serializers.ModelSerializer):
  class Meta:
    model = PageViews2
    field = ('pageViewId', 'pageViewURI', 'pageViewDateTime', 'pageViewSession')

