#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.db import models
from django.db import connection
from django.utils import timezone
from party.models import Party

from datetime import datetime

# Create your models here.
class NumericField(models.Field):
    def db_type(self, connection):
        return 'numeric'

class Subscription(models.Model):
    subscriptionId = models.AutoField(primary_key=True)
    partyId = models.ForeignKey("party.Party", null=True, db_column="partyId", related_name='party_id', on_delete=models.PROTECT)
    partnerId = models.ForeignKey("partner.Partner", null=True, db_column="partnerId", on_delete=models.PROTECT)
    startDate = models.DateTimeField(null=True)
    endDate = models.DateTimeField(null=True)
    consortiumStartDate = models.DateTimeField(null=True)
    consortiumEndDate = models.DateTimeField(null=True)
    consortiumId = models.ForeignKey("party.Party", null=True, on_delete=models.PROTECT)

    @staticmethod
    def getByIp(ipAddress):
        subscriptionList = []
        parties = Party.getByIp(ipAddress)
        return Subscription.objects.filter(partyId__in=parties)

    @staticmethod
    def getById(partyId):
        parties = Party.getById(partyId)
        return Subscription.objects.filter(partyId__in=parties)

    @staticmethod
    def filterActive(subscriptionQuerySet):
        now = timezone.now()
        return subscriptionQuerySet.filter(endDate__gt=now) \
                                   .filter(startDate__lt=now)

    @staticmethod
    def getActiveById(partyId, partnerId):
        subscriptionQuerySet = Subscription.getById(partyId) \
                                                   .filter(partnerId=partnerId)
        return Subscription.filterActive(subscriptionQuerySet)

    @staticmethod
    def getActiveByIp(ipAddress, partnerId):
        now = timezone.now()
        # get a list of subscription filtered by IP
        subscriptionQuerySet = Subscription.getByIp(ipAddress) \
                                           .filter(partnerId=partnerId)
        return Subscription.filterActive(subscriptionQuerySet)

    class Meta:
        db_table = "Subscription"
        unique_together = ("partyId", "partnerId")

class ActivationCode(models.Model):
    activationCodeId = models.AutoField(primary_key=True)
    activationCode = models.CharField(max_length=200, unique=True)
    partnerId = models.ForeignKey('partner.Partner', db_column="partnerId", on_delete=models.PROTECT)
    partyId = models.ForeignKey('party.Party', null=True, on_delete=models.PROTECT)
    period = models.IntegerField()
    purchaseDate = models.DateTimeField(default='2001-01-01T00:00:00Z')
    transactionType = models.CharField(max_length=200, null=True)
    deleteMarker = models.BooleanField(default=False)
    class Meta:
        db_table = "ActivationCode"

class SubscriptionTransaction(models.Model):
    subscriptionTransactionId = models.AutoField(primary_key=True)
    subscriptionId = models.ForeignKey('Subscription', db_column="subscriptionId", on_delete=models.PROTECT)
    transactionDate = models.DateTimeField(default='2000-01-01T00:00:00Z')
    startDate = models.DateTimeField(default='2001-01-01T00:00:00Z')
    endDate = models.DateTimeField(default='2020-01-01T00:00:00Z')
    transactionType = models.CharField(max_length=200)

    @staticmethod
    def createFromSubscription(subscription, transactionType, transactionStartDate=None, transactionEndDate=None):
        now = timezone.now()
        if not transactionStartDate:
            transactionStartDate = subscription.startDate
        if not transactionEndDate:
            transactionEndDate = subscription.endDate
        transactionJson = {
            'subscriptionId':subscription.subscriptionId,
            'transactionDate':now,
            'startDate':transactionStartDate,
            'endDate':transactionEndDate,
            'transactionType':transactionType,
        }
        from .serializers import SubscriptionTransactionSerializer
        transactionSerializer = SubscriptionTransactionSerializer(data=transactionJson)
        if transactionSerializer.is_valid():
            return transactionSerializer.save()
        # failed to create transaction
        return None

    class Meta:
        db_table = "SubscriptionTransaction"

class SubscriptionRequest(models.Model):
     subscriptionRequestId = models.AutoField(primary_key=True)
     requestDate = models.DateTimeField(default=datetime.now)
     firstName = models.CharField(max_length=32)
     lastName = models.CharField(max_length=32)
     email = models.CharField(max_length=128)
     institution = models.CharField(max_length=200)
     librarianName = models.CharField(max_length=100)
     librarianEmail = models.CharField(max_length=128)
     comments = models.CharField(max_length=5000)
     partnerId = models.ForeignKey('partner.Partner', max_length=200, db_column="partnerId", on_delete=models.PROTECT)
     requestType = models.CharField(max_length=32)

     class Meta:
        db_table = "SubscriptionRequest"