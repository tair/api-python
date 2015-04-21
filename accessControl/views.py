#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import generics
from services import MeteringService, SubscriptionService
from controls import AccessControl

from models import AccessType, AccessRule, Pattern
from serializers import AccessTypeSerializer, AccessRuleSerializer, PatternSerializer

# top level: /accessControls/

# /queries/
class Queries(APIView):
    availableQueries = {
        "ip",
        "partyId",
        "url",
    }
    def get(self, request, format=None):
        ip = None
        url = None
        partyId = None
        queries = self.availableQueries.intersection(set(request.query_params))
        for key in queries:
            value = request.GET.get(key)
            if key == 'ip':
                ip = value
            elif key == 'partyId':
                partyId = value
            elif key == 'url':
                url = value

        status = AccessControl.execute(ip, partyId, url)
        return HttpResponse('<html>%s %s</html>' % (status, ip))


# Basic CRUD operation for AccessType, AccessRule, and Pattern
class AccessTypeList(generics.ListCreateAPIView):
    queryset = AccessType.objects.all()
    serializer_class = AccessTypeSerializer

class AccessTypeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccessType.objects.all()
    serializer_class = AccessTypeSerializer

class AccessRuleList(generics.ListCreateAPIView):
    queryset = AccessRule.objects.all()
    serializer_class = AccessRuleSerializer

class AccessRuleDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccessRule.objects.all()
    serializer_class = AccessRuleSerializer

class PatternList(generics.ListCreateAPIView):
    queryset = Pattern.objects.all()
    serializer_class = PatternSerializer

class PatternDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pattern.objects.all()
    serializer_class = PatternSerializer
