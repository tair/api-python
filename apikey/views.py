#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.http import HttpResponse
from rest_framework import generics

from models import ApiKey
from serializers import ApiKeySerializer

import json

from common.views import GenericCRUDView

from rest_framework import status
from rest_framework.response import Response

# top level: /partners/


# Basic CRUD operation for Partner
# TODO: remove ApiKeyPermission from default permission_classes and set it in specific places using permission_classes param or decorator.
# /apikeys/
class ApiKeyCRUD(GenericCRUDView):
    queryset = ApiKey.objects.all()
    serializer_class = ApiKeySerializer
    http_method_names = ['get']
