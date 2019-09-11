import django
import sys
from django.test import TestCase
from .models import ApiKey
from common.tests import TestGenericInterfaces

genericForcePost = TestGenericInterfaces.forcePost

class ApiKeySample():
    path = 'apikeys/'
    url = None
    data = {
        'apiKey':'proxyKey',
    }
    updateData = {
        'apiKey':'proxyKey2',
    }
    pkName = 'apiKeyId'
    model = ApiKey

    def __init__(self, serverUrl):
        self.url = serverUrl + self.path

    def forcePost(self, data):
        return genericForcePost(self.model, self.pkName, data)
