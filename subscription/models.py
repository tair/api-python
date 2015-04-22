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
    class Meta:
        db_table = "Party"

class Payment(models.Model):
    paymentId = models.AutoField(primary_key=True)
    partyId = models.ForeignKey('Subscription', null=True, db_column="partyId")
    class Meta:
        db_table = "Payment"

class Subscription(models.Model):
    partyId = models.ForeignKey("Party", null=True, db_column="partyId")
    subscriptionTermId = models.ForeignKey('SubscriptionTerm', default=1, db_column="subscriptionTermId")
    startDate = models.DateTimeField(default='2000-01-01T00:00:00Z')
    endDate = models.DateTimeField(default='2012-12-21T00:00:00Z')

    @staticmethod
    def getByIp(ipAddress):
        subscriptionList = []
        ipRanges = SubscriptionIpRange.getByIp(ipAddress)
        for ipRange in ipRanges:
            # since ipRange.partyId is foreign key to Subscription,
            # ipRange.partyId returns a subscription object
            subscriptionList.append(ipRange.partyId)
        return subscriptionList

    @staticmethod
    def getActiveById(partyId):
        now = datetime.datetime.now()
        query = "SELECT COUNT(*) FROM Subscription " \
                "INNER JOIN Payment " \
                "USING (partyId) " \
                "WHERE Subscription.partyId = %s " \
                "AND Subscription.endDate > %s "
        cursor = connection.cursor()
        cursor.execute(query, (partyId, now))
        row = cursor.fetchone()
        return row[0] > 0

    @staticmethod
    def getActiveByIp(ipAddress):
        now = timezone.now()

        # get a list of subscription filtered by IP
        subscriptionListByIp = Subscription.getByIp(ipAddress)
        for obj in subscriptionListByIp:
            if obj.endDate > now:
                return True
        return False

    class Meta:
        db_table = "Subscription"

class SubscriptionIpRange(models.Model):
    subscriptionIpRangeId = models.AutoField(primary_key=True)
    start = models.GenericIPAddressField()
    end = models.GenericIPAddressField()
    partyId = models.ForeignKey('Subscription', db_column="partyId")

    @staticmethod
    def getByIp(ipAddress):
        objList = []
        objs = SubscriptionIpRange.objects.all()
        inputIpAddress = IPAddress(ipAddress)
        # for detail on comparison between IPAddress objects, see Python netaddr module.
        for obj in objs:
            start = IPAddress(obj.start)
            end = IPAddress(obj.end)
            if inputIpAddress > start and inputIpAddress < end:
                objList.append(obj)
        return objList

    class Meta:
        db_table = "SubscriptionIpRange"

class SubscriptionTerm(models.Model):
    subscriptionTermId = models.AutoField(primary_key=True)
    period = models.CharField(max_length=200)
    price = models.DecimalField(decimal_places=2,max_digits=6)
    groupDiscountPercentage = models.DecimalField(decimal_places=2,max_digits=6)
    autoRenew = models.BooleanField(default=False)

    @staticmethod
    def getByPartyId(partyId):
        query = "SELECT * FROM SubscriptionTerm " \
                "INNER JOIN Subscription " \
                "USING (subscriptionTermId) " \
                "WHERE Subscription.partyId = %s "
        return SubscriptionTerm.objects.raw(query, [partyId])

    class Meta:
        db_table = "SubscriptionTerm"
