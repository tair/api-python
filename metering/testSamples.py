import django
import copy
from metering.models import IpAddressCount, LimitValue, MeterBlacklist
from partner.models import Partner
from common.tests import TestGenericInterfaces

genericForcePost = TestGenericInterfaces.forcePost

class LimitValueSample():
    path = 'meters/limits/'
    url = None
    UNDER_LIMIT_VAL = 5
    WARNING_LIMIT_VAL = 10
    BLOCKING_LIMIT_VAL = 20
    INCREASE_BLOCKING_LIMIT_VAL = 30
    TYPE_WARNING = 'Warning'
    TYPE_EXCEED = 'Block'
    data = {
        'val': BLOCKING_LIMIT_VAL,
        'partnerId': None,
    }
    updateData = {
        'val': INCREASE_BLOCKING_LIMIT_VAL,
        'partnerId': None,
    }
    pkName = 'limitId'
    model = LimitValue

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path
        # create instance data
        self.data = copy.deepcopy(self.data)

    def setLimitVal(self, val):
        self.data['val'] = val

    def setPartnerId(self, partnerId):
        self.data['partnerId'] = partnerId

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partnerId'] = Partner.objects.get(partnerId=data['partnerId'])
        return genericForcePost(self.model, self.pkName, postData)

class IpAddressCountSample():
    path = 'meters/'
    url = None
    UNDER_LIMIT_IP = '123.45.6.7'
    WARNING_HIT_IP = '123.45.6.8'
    BLOCKING_HIT_IP = '123.45.6.9'
    data = {
        'ip': UNDER_LIMIT_IP,
        'count': LimitValueSample.UNDER_LIMIT_VAL,
        'partnerId': None,
    }
    updateData = {
        'ip': UNDER_LIMIT_IP,
        'count': LimitValueSample.BLOCKING_LIMIT_VAL,
        'partnerId': None,
    }
    pkName = 'id'
    model = IpAddressCount

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path
        self.data = copy.deepcopy(self.data)

    def setPartnerId(self, partnerId):
        self.data['partnerId'] = partnerId

    def setCount(self, count):
        self.data['count'] = count

    def setIp(self, ip):
        self.data['ip'] = ip

    def getCount(self):
        return self.data['count']

    def getIp(self):
        return self.data['ip']

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partnerId'] = Partner.objects.get(partnerId=data['partnerId'])
        return genericForcePost(self.model, self.pkName, postData)

class MeterBlacklistSample():
    path = 'meters/meterblacklist/'  
    url = None
    UNBLOCKED_URI = 'test_uri_unblocked'
    BLOCKED_URI = 'test_uri_blocked'
    BLOCKED_URI_II = 'test_uri_blocked_II'
    data = {
        'pattern': BLOCKED_URI,
        'partnerId': None
    }
    updateData = {
        'pattern': BLOCKED_URI_II,
        'partnerId': None
    }
    pkName = 'meterBlackListId'
    model = MeterBlacklist

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path
        self.data = copy.deepcopy(self.data)

    def setPartnerId(self, partnerId):
        self.data['partnerId'] = partnerId

    def setPattern(self, pattern):
        self.data['pattern'] = pattern

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        # partnerId for MeterBlacklist model is not foreign key
        return genericForcePost(self.model, self.pkName, postData)
