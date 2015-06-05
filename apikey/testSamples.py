import django
import unittest
import sys, getopt
from unittest import TestCase
from models import ApiKey

from common.pyTests import PyTestGenerics

genericForcePost = PyTestGenerics.forcePost

class ApiKeySample():
    path = 'apikeys/'
    url = None
    data = {
        'apiKey':'proxyKey',
    }
    updateData = {
        'apiKey':'proxy2Key',
    }
    pkName = 'apiKeyId'
    model = ApiKey

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        return genericForcePost(self.model, self.pkName, data)
