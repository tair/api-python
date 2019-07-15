#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.db import models
from django.db import connection
from netaddr import IPAddress
from django.utils import timezone
from django.apps import apps
from common.common import validateIpRange

import logging
logger = logging.getLogger('phoenix.api.party')

# Create your models here.
class NumericField(models.Field):
    def db_type(self, connection):
        return 'numeric'

class Party(models.Model):
    partyId = models.AutoField(primary_key=True)
    partyType = models.CharField(max_length=200, default='user')
    name = models.CharField(max_length=200, default='')
    display = models.BooleanField(default=True)
    country = models.ForeignKey('Country', null=True, db_column="countryId")
    consortiums = models.ManyToManyField('self', through="PartyAffiliation", through_fields=('childPartyId', 'parentPartyId'), symmetrical=False, related_name="PartyAffiliation")
    label = models.CharField(max_length=64, null=True)

    # cascade delete - http://stackoverflow.com/questions/12754024/onetoonefield-and-deleting
    # circular import solution - http://stackoverflow.com/questions/29744016/how-to-lazy-load-a-model-in-a-managers-to-stop-circular-imports
    # TODO: learn post_delete and add it for Credential in case there will be bulk delete
    def delete(self):
        credentialModel = apps.get_model('authentication', 'Credential')
        credentialModel.objects.get(partyId = self).delete()
        return super(Party, self).delete()

    @staticmethod
    def getByIp(ipAddress):
        partyList = []
        ipRanges = IpRange.getByIp(ipAddress)
        for ipRange in ipRanges:
            partyId = ipRange.partyId.partyId
            consortiums = Party.objects.all().get(partyId = partyId).consortiums.values_list('partyId', flat=True)
            partyList.append(partyId)
            partyList.extend(consortiums)
        return partyList

    @staticmethod
    def getById(partyId):
        partyList = []
        consortiums = Party.objects.all().get(partyId = partyId).consortiums.values_list('partyId', flat=True)
        partyList.append(partyId)
        partyList.extend(consortiums)
        return partyList

    class Meta:
        db_table = "Party"

class PartyAffiliation(models.Model):
    partyAffiliationId = models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)
    childPartyId = models.ForeignKey(Party, related_name="childPartyId", db_column="childPartyId")
    parentPartyId = models.ForeignKey(Party, related_name="parentPartyId", db_column="parentPartyId")

    class Meta:
        db_table = "PartyAffiliation"
        unique_together = ("childPartyId", "parentPartyId")

class IpRange(models.Model):
    ipRangeId = models.AutoField(primary_key=True)
    start = models.GenericIPAddressField()
    end = models.GenericIPAddressField()
    partyId = models.ForeignKey('Party', db_column="partyId")
    label = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        db_table = "IpRange"

    def clean(self, *args, **kwargs):
        validateIpRange(self.start, self.end)
        super(IpRange, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.clean()
        super(IpRange, self).save(*args, **kwargs)

    @staticmethod
    def getByIp(ipAddress):
        objList = []
        objs = IpRange.objects.all()
        try:
            inputIpAddress = IPAddress(ipAddress)
        except Exception:
            logger.error("Party IpRange %s, %s" % (ipAddress, "invalid ip"))
            pass
        # for detail on comparison between IPAddress objects, see Python netaddr module.
        for obj in objs:
            try:
                start = IPAddress(obj.start)
            except Exception:
                logger.error("Party IpRange %s, %s" % (obj.start, "invalid start ip"))
                pass
            try:
                end = IPAddress(obj.end)
            except Exception:
                logger.error("Party IpRange %s, %s" % (obj.end, "invalid end ip"))
                pass
            
            if inputIpAddress >= start and inputIpAddress <= end:
                objList.append(obj)
        return objList

class Country(models.Model):
    countryId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)

    class Meta:
        db_table = "Country"

class ImageInfo(models.Model):
    imageInfoId = models.AutoField(primary_key=True);
    partyId = models.ForeignKey(Party, db_column="partyId")
    name = models.CharField(max_length=200)
    imageUrl = models.CharField(max_length=500)
    createdAt = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "ImageInfo"