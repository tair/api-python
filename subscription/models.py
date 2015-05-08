#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.db import models
from django.db import connection
from netaddr import IPAddress
from django.utils import timezone
import datetime

# Create your models here.
class NumericField(models.Field):
    def db_type(self, connection):
        return 'numeric'

class Party(models.Model):
    partyId = models.AutoField(primary_key=True)
    partyType = models.CharField(max_length=200, default='user')

    @staticmethod
    def getByIp(ipAddress):
        partyList = []
        ipRanges = IpRange.getByIp(ipAddress)
        for ipRange in ipRanges:
            partyId = ipRange.partyId
            partyList.append(partyId)
        return partyList

    class Meta:
        db_table = "Party"

class Subscription(models.Model):
    subscriptionId = models.AutoField(primary_key=True)
    partyId = models.ForeignKey("Party", null=True, db_column="partyId")
    partnerId = models.ForeignKey("partner.Partner", null=True, db_column="partnerId")
    startDate = models.DateTimeField(default='2000-01-01T00:00:00Z')
    endDate = models.DateTimeField(default='2012-12-21T00:00:00Z')

    @staticmethod
    def getByIp(ipAddress):
        subscriptionList = []
        parties = Party.getByIp(ipAddress)
        for party in parties:
            subscriptions = Subscription.objects.filter(partyId=party)
            for item in subscriptions:
                subscriptionList.append(item)

        return subscriptionList

    @staticmethod
    def getActiveById(partyId):
        now = datetime.datetime.now()
        return Subscription.objects.all() \
                                   .filter(partyId=partyId) \
                                   .filter(endDate__gt=now) \
                                   .filter(startDate__lt=now) 

    @staticmethod
    def getActiveByIp(ipAddress):
        now = timezone.now()

        # get a list of subscription filtered by IP
        subscriptionListByIp = Subscription.getByIp(ipAddress)
        objList = []
        for obj in subscriptionListByIp:
            if obj.endDate > now and obj.startDate < now:
                objList.append(obj)
        return objList

    class Meta:
        db_table = "SubscriptionState"

class SubscriptionTransaction(models.Model):
    subscriptionTransactionId = models.AutoField(primary_key=True)
    subscriptionId = models.ForeignKey('Subscription', db_column="subscriptionId")
    transactionDate = models.DateTimeField(default='2000-01-01T00:00:00Z')
    startDate = models.DateTimeField(default='2001-01-01T00:00:00Z')
    endDate = models.DateTimeField(default='2020-01-01T00:00:00Z')
    transactionType = models.CharField(max_length=200)

    class Meta:
        db_table = "SubscriptionTransaction"

class IpRange(models.Model):
    ipRangeId = models.AutoField(primary_key=True)
    start = models.GenericIPAddressField()
    end = models.GenericIPAddressField()
    partyId = models.ForeignKey('Party', db_column="partyId")

    @staticmethod
    def getByIp(ipAddress):
        objList = []
        objs = IpRange.objects.all()
        inputIpAddress = IPAddress(ipAddress)
        # for detail on comparison between IPAddress objects, see Python netaddr module.
        for obj in objs:
            start = IPAddress(obj.start)
            end = IPAddress(obj.end)
            if inputIpAddress > start and inputIpAddress < end:
                objList.append(obj)
        return objList

    class Meta:
        db_table = "IpRange"
