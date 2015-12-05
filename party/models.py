#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.db import models
from django.db import connection
from netaddr import IPAddress
from django.utils import timezone

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
    consortiums = models.ManyToManyField('self', through="Affiliation", through_fields=("institutionId", "consortiumId"))

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

class Affiliation(models.Model):
    institutionId = models.ForeignKey(Party, related_name="institutionId")
    consortiumId = models.ForeignKey(Party, related_name="consortiumId")

class IpRange(models.Model):
    ipRangeId = models.AutoField(primary_key=True)
    start = models.GenericIPAddressField()
    end = models.GenericIPAddressField()
    partyId = models.ForeignKey('Party', db_column="partyId")
    label = models.CharField(max_length=64, null=True)

    @staticmethod
    def getByIp(ipAddress):
        objList = []
        objs = IpRange.objects.all()
        inputIpAddress = IPAddress(ipAddress)
        # for detail on comparison between IPAddress objects, see Python netaddr module.
        for obj in objs:
            start = IPAddress(obj.start)
            end = IPAddress(obj.end)
            if inputIpAddress >= start and inputIpAddress <= end:
                objList.append(obj)
        return objList

    class Meta:
        db_table = "IpRange"

class Country(models.Model):
    countryId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)

    class Meta:
        db_table = "Country"
