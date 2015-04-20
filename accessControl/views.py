#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.http import HttpResponse
from rest_framework.views import APIView
from services import MeteringService, SubscriptionService
from controls import AccessControl

# top level: /accessControls/

# /queries/
class Queries(APIView):
    availableQueries = {
        "ip",
        "partyId",
    }
    def get(self, request, format=None):
        ip = '125.4.5.67'
        queries = self.availableQueries.intersection(set(request.query_params))
        for key in queries:
            value = request.GET.get(key)
            if key == 'ip':
                ip = value

        status = AccessControl.execute(ip, 'cat')
        return HttpResponse('<html>%s %s</html>' % (status, ip))
