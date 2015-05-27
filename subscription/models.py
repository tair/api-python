#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.db import models
from django.db import connection
from django.utils import timezone
from party.models import Party

# Create your models here.
class NumericField(models.Field):
    def db_type(self, connection):
        return 'numeric'

class Subscription(models.Model):
    subscriptionId = models.AutoField(primary_key=True)
    partyId = models.ForeignKey("party.Party", null=True, db_column="partyId")
    partnerId = models.ForeignKey("partner.Partner", null=True, db_column="partnerId")
    startDate = models.DateTimeField(default='2000-01-01T00:00:00Z')
    endDate = models.DateTimeField(default='2012-12-21T00:00:00Z')

    @staticmethod
    def getByIp(ipAddress):
        subscriptionList = []
        parties = Party.getByIp(ipAddress)
        return Subscription.objects.filter(partyId__in=parties)

    @staticmethod
    def filterActive(subscriptionQuerySet):
        now = timezone.now()
        return subscriptionQuerySet.filter(endDate__gt=now) \
                                   .filter(startDate__lt=now)

    @staticmethod
    def getActiveById(partyId):
        subscriptionQuerySet = Subscription.objects.all() \
                                                   .filter(partyId=partyId)
        return Subscription.filterActive(subscriptionQuerySet)

    @staticmethod
    def getActiveByIp(ipAddress):
        now = timezone.now()

        # get a list of subscription filtered by IP
        subscriptionQuerySet = Subscription.getByIp(ipAddress)
        return Subscription.filterActive(subscriptionQuerySet)

    class Meta:
        db_table = "Subscription"

class SubscriptionTransaction(models.Model):
    subscriptionTransactionId = models.AutoField(primary_key=True)
    subscriptionId = models.ForeignKey('Subscription', db_column="subscriptionId")
    transactionDate = models.DateTimeField(default='2000-01-01T00:00:00Z')
    startDate = models.DateTimeField(default='2001-01-01T00:00:00Z')
    endDate = models.DateTimeField(default='2020-01-01T00:00:00Z')
    transactionType = models.CharField(max_length=200)

    @staticmethod
    def createFromSubscription(subscription, transactionType):
        now = timezone.now()
        transactionJson = {
            'subscriptionId':subscription.subscriptionId,
            'transactionDate':now,
            'startDate':subscription.startDate,
            'endDate':subscription.endDate,
            'transactionType':transactionType,
        }
        from serializers import SubscriptionTransactionSerializer
        transactionSerializer = SubscriptionTransactionSerializer(data=transactionJson)
        if transactionSerializer.is_valid():
            return transactionSerializer.save()
        # failed to create transaction
        return None
        
    class Meta:
        db_table = "SubscriptionTransaction"

