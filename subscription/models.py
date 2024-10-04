#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.db import models
from django.db.models import Sum
from django.db import connection
from django.utils import timezone
from datetime import timedelta
from party.models import Party
from authorization.models import UriPattern
from datetime import datetime

# Create your models here.
class NumericField(models.Field):
    def db_type(self, connection):
        return 'numeric'

class UserBucketUsage(models.Model):
    user_usage_id = models.AutoField(primary_key=True)
    partyId = models.OneToOneField("party.Party", null=True, on_delete=models.SET_NULL, db_column="partyId_id", related_name='user_bucket_usage')
    total_units = models.IntegerField(null=False)
    remaining_units = models.IntegerField(null=False)
    expiry_date = models.DateTimeField(null=False)
    partner_id = models.CharField(max_length=200, null=False)

    class Meta:
        db_table = 'UserBucketUsage'

class PremiumUsageUnits(models.Model):
    id = models.AutoField(primary_key=True)
    pattern_object = models.ForeignKey(UriPattern, on_delete=models.CASCADE, db_column='patternId')  
    units_consumed = models.IntegerField()

    class Meta:
        db_table = 'PremiumUsageUnits'

class BucketTransaction(models.Model):
    bucket_transaction_id = models.AutoField(primary_key=True)
    transaction_date = models.DateTimeField(null=False)
    partyId_purchased = models.ForeignKey("party.Party", on_delete=models.CASCADE, db_column="partyId_purchased")
    bucket_type_id = models.IntegerField(null=False)
    activation_code_id = models.IntegerField(null=False)
    units_per_bucket = models.IntegerField(null=False)
    transaction_type = models.CharField(max_length=200, null=False)

    class Meta:
        db_table = 'BucketTransaction'

class Subscription(models.Model):
    subscriptionId = models.AutoField(primary_key=True)
    partyId = models.ForeignKey("party.Party", null=True, db_column="partyId", related_name='party_id')
    partnerId = models.ForeignKey("partner.Partner", null=True, db_column="partnerId")
    startDate = models.DateTimeField(null=True)
    endDate = models.DateTimeField(null=True)
    consortiumStartDate = models.DateTimeField(null=True)
    consortiumEndDate = models.DateTimeField(null=True)
    consortiumId = models.ForeignKey("party.Party", null=True)

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
    partnerId = models.ForeignKey('partner.Partner', db_column="partnerId")
    partyId = models.ForeignKey('party.Party', null=True)
    period = models.IntegerField()
    purchaseDate = models.DateTimeField(default='2001-01-01T00:00:00Z')
    transactionType = models.CharField(max_length=200, null=True)
    deleteMarker = models.BooleanField(default=False)
    class Meta:
        db_table = "ActivationCode"

class SubscriptionTransaction(models.Model):
    subscriptionTransactionId = models.AutoField(primary_key=True)
    subscriptionId = models.ForeignKey('Subscription', db_column="subscriptionId")
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
        from serializers import SubscriptionTransactionSerializer
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
     partnerId = models.ForeignKey('partner.Partner', max_length=200, db_column="partnerId")
     requestType = models.CharField(max_length=32)

     class Meta:
        db_table = "SubscriptionRequest"

class UsageUnitPurchase(models.Model):
    purchaseId = models.AutoField(primary_key=True)
    partyId = models.ForeignKey("party.Party", null=False, db_column="partyId")
    partnerId = models.ForeignKey("partner.Partner", null=False, db_column="partnerId")
    quantity = models.IntegerField()
    purchaseDate = models.DateTimeField(null=False)
    transactionId = models.CharField(max_length=64, null=True, unique=True)
    syncedToPartner = models.BooleanField(default=False)

    @staticmethod
    def getByIdAndPartner(partyId, partnerId):
        parties = Party.getById(partyId)
        return UsageUnitPurchase.objects.filter(partyId__in=parties) \
                                .filter(partnerId=partnerId) \

    @staticmethod
    def getActiveByIdAndPartner(partyId, partnerId, validDuration):
        validStartDate = timezone.now() - timedelta(days=validDuration)
        return UsageUnitPurchase.getByIdAndPartner(partyId, partnerId) \
                                .filter(purchaseDate__gte=validStartDate)

    @staticmethod
    def getActiveUnitSumByIdAndPartner(partyId, partnerId, validDuration):
        units = UsageUnitPurchase.getActiveByIdAndPartner(partyId, partnerId, validDuration)
        totalUnitSum = units.aggregate(Sum('quantity'))
        if totalUnitSum['quantity__sum']:
            return totalUnitSum['quantity__sum']
        else:
            return 0

    class Meta:
        db_table = "UsageUnitPurchase"

class UsageTierTerm(models.Model):
    tierId = models.AutoField(primary_key=True)
    partnerId = models.ForeignKey("partner.Partner", null=False, db_column="partnerId")
    name = models.CharField(max_length=20)
    label = models.CharField(max_length=20)
    price = models.IntegerField(null=False)
    description = models.CharField(max_length=200)
    isAcademic = models.BooleanField(null=False, default=False)
    durationInDays = models.IntegerField(null=False)

    @staticmethod
    def getByPartner(partnerId):
        return UsageTierTerm.objects.filter(partnerId=partnerId)

    class Meta:
        db_table = "UsageTierTerm"

class UsageTierPurchase(models.Model):
    purchaseId = models.AutoField(primary_key=True)
    partyId = models.ForeignKey("party.Party", null=False, db_column="partyId")
    partnerId = models.ForeignKey("partner.Partner", null=False, db_column="partnerId")
    tierId = models.ForeignKey("subscription.UsageTierTerm", null=False, db_column="tierId")
    purchaseDate = models.DateTimeField(null=False, default=datetime.now)
    expirationDate = models.DateTimeField(null=False)
    transactionId = models.CharField(max_length=64, null=True, unique=True)
    syncedToPartner = models.BooleanField(default=False)
    partnerUUID = models.CharField(max_length=64, null=True, unique=True)

    @staticmethod
    def getByIdAndPartner(partyId, partnerId):
        try:
            return UsageTierPurchase.objects.filter(partyId=partyId).filter(partnerId=partnerId)
        except Party.MultipleObjectsReturned:
            pass
        except Party.DoesNotExist:
            pass

    @staticmethod
    def getActiveByIdAndPartner(partyId, partnerId):
        now = timezone.now()
        return UsageTierPurchase.getByIdAndPartner(partyId, partnerId) \
                                .filter(purchaseDate__lte=now) \
                                .filter(expirationDate__gte=now)

    def getByPartnerUUID(partner, uuid):
        return UsageTierPurchase.objects.filter(partnerUUID=uuid).filter(partnerId=partnerId)

    class Meta:
        db_table = "UsageTierPurchase"

class UsageAddonOption(models.Model):
    optionId = models.AutoField(primary_key=True)
    partnerId = models.ForeignKey("partner.Partner", null=False, db_column="partnerId")
    partnerUUID = models.CharField(max_length=64)
    quantity = models.IntegerField()
    unit = models.CharField(max_length=20)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=200)
    durationInDays = models.IntegerField(null=False)
    proportional = models.BooleanField(null=False, default=True)

    @staticmethod
    def getByPartner(partnerId):
        return UsageAddonOption.objects.filter(partnerId=partnerId)

    class Meta:
        db_table = "UsageAddonOption"

class UsageAddonPricing(models.Model):
    pricingId = models.AutoField(primary_key=True)
    # need related_name for nested serializer reference
    optionId = models.ForeignKey("subscription.UsageAddonOption", null=False, db_column="optionId", related_name="pricing")
    price = models.IntegerField()
    priority = models.IntegerField()
    threshold = models.IntegerField()

    @staticmethod
    def getByOption(optionId):
        return UsageAddonPricing.objects.filter(optionId=optionId).order_by(priority)

    class Meta:
        db_table = "UsageAddonPricing"
        ordering = ['priority']

class UsageAddonPurchase(models.Model):
    purchaseId = models.AutoField(primary_key=True)
    partyId = models.ForeignKey("party.Party", null=False, db_column="partyId")
    partnerId = models.ForeignKey("partner.Partner", null=False, db_column="partnerId")
    optionId = models.ForeignKey("subscription.UsageAddonOption", null=False, db_column="optionId")
    partnerSubscriptionUUID = models.CharField(max_length=64, null=False)
    optionItemQty = models.IntegerField() # the number of add on term item purchased
    purchaseDate = models.DateTimeField(null=False, default=datetime.now)
    expirationDate = models.DateTimeField(null=False)
    transactionId = models.CharField(max_length=64, null=True, unique=True)
    amountPaid = models.DecimalField(max_digits=10, decimal_places=2)

    @staticmethod
    def getByIdAndPartner(partyId, partnerId):
        try:
            return UsageAddonPurchase.objects.filter(partyId=partyId).filter(partnerId=partnerId)
        except Party.MultipleObjectsReturned:
            pass
        except Party.DoesNotExist:
            pass

    @staticmethod
    def getActiveByIdAndPartner(partyId, partnerId, validDuration):
        validStartDate = timezone.now() - timedelta(days=validDuration)
        return UsageAddonPurchase.getByIdAndPartner(partyId, partnerId) \
                                .filter(purchaseDate__gte=validStartDate)

    class Meta:
        db_table = "UsageAddonPurchase"

# This class obj will only be created & saved when synchronized to partner, so no need for sync flag
class UsageAddonPurchaseSync(models.Model):
    purchaseId = models.ForeignKey("subscription.UsageAddonPurchase", null=False, db_column="purchaseId")
    partnerUUID = models.CharField(max_length=64)

    @staticmethod
    def getSyncById(purchaseId):
        return UsageAddonPurchaseSync.objects.filter(purchaseId=purchaseId)

    @staticmethod
    def getAllUnsyncedPurchases():
        return UsageAddonPurchaseSync.objects.filter(syncedToPartner=False)

    @staticmethod
    def getIsAllSynced():
        if not getAllUnsyncedPurchases():
            return True
        else:
            return False

    @staticmethod
    def getIsPurchaseSyncedById(purchaseId):
        if UsageAddonPurchaseSync.objects.filter(purchaseId=purchaseId).filter(syncedToPartner=False):
            return False
        else:
            return True

    @staticmethod
    def getUnsyncedPurchaseById(purchaseId):
        return UsageAddonPurchaseSync.objects.filter(purchaseId=purchaseId).filter(syncedToPartner=False)

    class Meta:
        db_table = "UsageAddonPurchaseSync"