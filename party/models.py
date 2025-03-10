#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.db import models
from django.db import connection
from netaddr import IPAddress
from django.utils import timezone
from common.common import validateIpRange
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from common.common import ip2long, is_valid_ipv4

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
    serialId = models.CharField(max_length=16, unique=True, null=True)

    class Meta:
        db_table = "Party"

    def clean(self, *args, **kwargs):
        self.validateInstitutionCountry()
        super(Party, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.clean()
        super(Party, self).save(*args, **kwargs)

    @staticmethod
    def getByIp(ipAddress):
        partyList = []
        ipRanges = ActiveIpRange.getByIp(ipAddress)
        for ipRange in ipRanges:
            partyId = ipRange.partyId.partyId
            consortiums = Party.objects.all().get(partyId = partyId).consortiums.values_list('partyId', flat=True)
            partyList.append(partyId)
            partyList.extend(consortiums)
        return partyList

    @staticmethod
    def getById(partyId):
        try:
            partyList = []
            party = Party.objects.get(partyId=partyId)
            consortiums = party.consortiums.values_list('partyId', flat=True)
            partyList.append(partyId)
            partyList.extend(consortiums)
            return partyList
        except ObjectDoesNotExist:
            return []
    
    def validateInstitutionCountry(self):
        if self.partyType == 'organization':
            if not self.country:
                raise serializers.ValidationError({'Party': _('Country field is required')})


class PartyAffiliation(models.Model):
    partyAffiliationId = models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)
    childPartyId = models.ForeignKey(Party, related_name="childPartyId", db_column="childPartyId")
    parentPartyId = models.ForeignKey(Party, related_name="parentPartyId", db_column="parentPartyId")

    class Meta:
        db_table = "PartyAffiliation"
        unique_together = ("childPartyId", "parentPartyId")

# note that startLong and endLong does not work for IPV6 addresses
class IpRange(models.Model):
    ipRangeId = models.AutoField(primary_key=True)
    start = models.GenericIPAddressField()
    end = models.GenericIPAddressField()
    startLong = models.BigIntegerField()
    endLong = models.BigIntegerField()
    partyId = models.ForeignKey('Party', db_column="partyId")
    label = models.CharField(max_length=64, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    expiredAt = models.DateTimeField(null=True)

    class Meta:
        db_table = "IpRange"

    def clean(self, *args, **kwargs):
        validateIpRange(self.start, self.end, self.ipRangeId, type(self))
        super(IpRange, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.clean()
        self.startLong = ip2long(self.start)
        self.endLong = ip2long(self.end)
        super(IpRange, self).save(*args, **kwargs)

    @staticmethod
    def getAllIPV6Objects():
        ipv4_max_long = 4294967295
        return IpRange.objects.all().filter(startLong__gt=ipv4_max_long)

class Country(models.Model):
    countryId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    abbreviation = models.CharField(max_length=2)

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

# note that startLong and endLong does not work for IPV6 addresses
class ActiveIpRange(models.Model):
    ipRangeId = models.AutoField(primary_key=True)
    start = models.GenericIPAddressField()
    end = models.GenericIPAddressField()
    startLong = models.BigIntegerField()
    endLong = models.BigIntegerField()
    partyId = models.ForeignKey('Party', db_column="partyId")
    label = models.CharField(max_length=64, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    expiredAt = models.DateTimeField(null=True)

    class Meta:
        managed = False
        db_table = 'ActiveIpRange'

    @staticmethod
    def getAllIPV6Objects():
        ipv4_max_long = 4294967295
        return ActiveIpRange.objects.all().filter(startLong__gt=ipv4_max_long)

    @staticmethod
    def getByIp(ipAddress):
        objList = []
        try:
            inputIpAddress = IPAddress(ipAddress)
        except Exception:
            logger.error("Party IpRange %s, %s" % (ipAddress, "invalid ip"))
            pass
        if is_valid_ipv4(ipAddress):
            ip_long = ip2long(ipAddress)
            return ActiveIpRange.objects.all().filter(startLong__lte=ip_long).filter(endLong__gte=ip_long)
        # ipv6
        else:    
            # for detail on comparison between IPAddress objects, see Python netaddr module.
            objs = ActiveIpRange.getAllIPV6Objects()
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