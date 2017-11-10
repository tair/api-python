#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.


from loggingapp.models import PageView
from rest_framework import serializers

class PageViewSerializer(serializers.ModelSerializer):
  class Meta:
    model = PageView
    field = ('pageViewId', 'uri', 'pageViewDate', 'partyId', 'sessionId', 'ip', 'ipList')

