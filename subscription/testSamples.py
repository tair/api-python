import copy
from subscription.models import Subscription, SubscriptionTransaction, ActivationCode
from party.models import Party
from partner.models import Partner
from datetime import timedelta
from django.utils import timezone
from common.tests import TestGenericInterfaces

genericForcePost = TestGenericInterfaces.forcePost

NUM_DAYS_AFTER_PURCHASE = 2
NUM_SUBSCRIBED_DAYS = 30
UPDATE_NUM_DAYS_AFTER_PURCHASE = 1
UPDATE_NUM_SUBSCRIBED_DAYS = 60

def getDateTimeString(dateTimeObj):
    return dateTimeObj.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

class ActivationCodeSample():
    path = 'subscriptions/activationCodes/'
    url = None
    TRANSACTION_TYPE = 'create_free'
    data = {
        'activationCode':'testactivationcode',
        'partnerId':None,
        # partyId is assigned upon activation not on creation
        # 'partyId':None,
        'period':NUM_SUBSCRIBED_DAYS,
        'purchaseDate':None,
    }
    updateData = {
        'activationCode':'testactivationcode2',
        'partnerId':None,
        # 'partyId':None,
        'period':UPDATE_NUM_SUBSCRIBED_DAYS,
        'purchaseDate':None,
    }
    pkName = 'activationCodeId'
    model = ActivationCode

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path
        self.data['purchaseDate'] = getDateTimeString(timezone.now() - timedelta(days=NUM_DAYS_AFTER_PURCHASE))
        self.updateData['purchaseDate'] = getDateTimeString(timezone.now() - timedelta(days=UPDATE_NUM_DAYS_AFTER_PURCHASE))

    def setPartnerId(self, partnerId):
        self.data['partnerId'] = partnerId

    # for get endpoint transactionType is not returned, so we only initialize this param when needed
    def initTransctionType(self):
        self.data['transactionType'] = self.TRANSACTION_TYPE

    def getActivationCode(self):
        return self.data['activationCode']

    def getPeriod(self):
        return self.data['period']

    def getTransactionType(self):
        return self.data['transactionType']

    def getPartnerId(self):
        return self.data['partnerId']

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partnerId'] = Partner.objects.get(partnerId=data['partnerId'])
        return genericForcePost(self.model, self.pkName, postData)

class SubscriptionSample():
    path = 'subscriptions/'
    url = None
    data = {
        'startDate':None,
        'endDate':None,
        'partnerId':None,
        'partyId':None,
    }
    updateData = {
        'startDate':None,
        'partnerId':None,
        'partyId':None,
    }
    pkName = 'subscriptionId'
    model = Subscription

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path
        self.data = copy.deepcopy(self.data)

        startDateObj = timezone.now() - timedelta(days=NUM_DAYS_AFTER_PURCHASE)
        self.data['startDate'] = getDateTimeString(startDateObj)
        self.data['endDate'] = getDateTimeString(startDateObj + timedelta(days=NUM_SUBSCRIBED_DAYS))

        updateStartDateObj = timezone.now() - timedelta(days=UPDATE_NUM_DAYS_AFTER_PURCHASE)
        self.updateData['startDate'] = getDateTimeString(updateStartDateObj)
        self.updateData['endDate'] = getDateTimeString(updateStartDateObj + timedelta(days=UPDATE_NUM_SUBSCRIBED_DAYS))

    def setPartnerId(self, partnerId):
        self.data['partnerId'] = partnerId

    def setPartyId(self, partyId):
        self.data['partyId'] = partyId

    def getEndDate(self):
        return self.data['endDate']

    def setAsExpired(self):
        self.data['startDate'] = getDateTimeString(timezone.now() - timedelta(days=2 * NUM_SUBSCRIBED_DAYS))
        self.data['endDate'] = getDateTimeString(timezone.now() - timedelta(days=NUM_SUBSCRIBED_DAYS))

    def forcePost(self,data):
        postData = copy.deepcopy(data)
        postData['partyId'] = Party.objects.get(partyId=data['partyId'])
        postData['partnerId'] = Partner.objects.get(partnerId=data['partnerId'])
        return genericForcePost(self.model, self.pkName, postData)

class SubscriptionTransactionSample():
    path = 'subscriptions/transactions/'
    url = None   
    data = {
        'transactionDate':None,
        'startDate':None,
        'endDate':None,
        'transactionType':'create',
    }
    updateData = {
        'transactionDate':None,
        'startDate':None,
        'endDate':None,
        'transactionType':'renew',
    }
    pkName = 'subscriptionTransactionId'
    model = SubscriptionTransaction

    def __init__(self, serverUrl):
        self.url = serverUrl+self.path

        transactionDateObj = timezone.now() - timedelta(days=NUM_DAYS_AFTER_PURCHASE)
        self.data['transactionDate'] = getDateTimeString(transactionDateObj)
        self.data['startDate'] = self.data['transactionDate']
        self.data['endDate'] = getDateTimeString(transactionDateObj + timedelta(days=NUM_SUBSCRIBED_DAYS))

        updateTransactionDateObj = timezone.now() - timedelta(days=UPDATE_NUM_DAYS_AFTER_PURCHASE)
        self.updateData['transactionDate'] = getDateTimeString(updateTransactionDateObj)
        self.updateData['startDate'] = self.updateData['transactionDate']
        self.updateData['endDate'] = getDateTimeString(updateTransactionDateObj + timedelta(days=UPDATE_NUM_DAYS_AFTER_PURCHASE))


    def forcePost(self,data):
        postData = copy.deepcopy(data)
        if ('subscriptionId' in postData):
            postData['subscriptionId'] = Subscription.objects.get(subscriptionId=postData['subscriptionId'])
        return genericForcePost(self.model, self.pkName, postData)
