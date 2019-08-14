import django
import unittest
import sys
import copy
from loggingapp.models import PageView
from party.models import Party
from partner.models import Partner
from django.test import TestCase
from common.tests import TestGenericInterfaces

genericForcePost = TestGenericInterfaces.forcePost

class PageViewSample():
    SESSION_ID_I = '9A417B49536A8395936C4717E80E005C'
    SESSION_ID_II = 'BC71B65BF137AD7924600A00D3F03C1C'
    SESSION_ID_III = '51AD64E5EDEF1C59CAF5C30EFA2F4783'
    path = 'session-logs/page-views/'
    url = None

    data = {
        'uri':'test_url_1',
        'partyId':None,
        'partnerId':None,
        'pageViewDate':'2018-08-31T00:00:00Z',
        'sessionId':SESSION_ID_I,
        'ip':'123.45.67.8',
        'ipList':'111.11.22.1, 123.45.67.8',
        'isPaidContent':False,
        'meterStatus':PageView.METER_NOT_METERED_STATUS

    }
    updateData = {
        'uri':'test_url_2',
        'partyId':None,
        'partnerId':None,
        'pageViewDate':'2019-08-31T17:34:26Z',
        'sessionId':SESSION_ID_II,
        'ip':'12.34.5.67',
        'ipList':'111.11.22.23, 123.45.67.8, 12.34.5.67',
        'isPaidContent':True,
        'meterStatus':PageView.METER_BLOCK_STATUS

    }
    pkName = 'pageViewId'
    model = PageView

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partyId'] = Party.objects.get(partyId=data['partyId'])
        postData['partnerId'] = Partner.objects.get(partnerId=data['partnerId'])
        return genericForcePost(self.model, self.pkName, postData)


