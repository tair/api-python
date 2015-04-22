#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import generics
from services import MeteringService, SubscriptionService
from controls import AccessControl

from models import AccessType, AccessRule, Pattern
from serializers import AccessTypeSerializer, AccessRuleSerializer, PatternSerializer

# top level: /accessControls/


# Main API call to access control service. Caller gives in partyId, and the
# service outputs access control status such as "OK", "Warn", "BlockBySubscription".

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

# /accessTypes/
class AccessTypesList(generics.ListCreateAPIView):
    queryset = AccessType.objects.all()
    serializer_class = AccessTypeSerializer

# /accessTypes/<primary-key>
class AccessTypesDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccessType.objects.all()
    serializer_class = AccessTypeSerializer

# /accessRules/
class AccessRulesList(generics.ListCreateAPIView):
    queryset = AccessRule.objects.all()
    serializer_class = AccessRuleSerializer

# /accessRules/<primary-key>
class AccessRulesDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccessRule.objects.all()
    serializer_class = AccessRuleSerializer

# /patterns/
class PatternsList(generics.ListCreateAPIView):
    queryset = Pattern.objects.all()
    serializer_class = PatternSerializer

# /patterns/<primary-key>
class PatternsDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pattern.objects.all()
    serializer_class = PatternSerializer
