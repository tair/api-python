#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.db import models
from django.db import connection
from netaddr import IPAddress
from django.utils import timezone
import logging
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
    label = models.CharField(max_length=64, null=True)

    @staticmethod
    def getByIp(ipAddress):
        dirname = os.path.dirname(os.path.realpath(__file__))
        logging.basicConfig(filename="%s/logs/invalidIP.log" % dirname,
                            format='%(asctime)s %(message)s')
        objList = []
        objs = IpRange.objects.all()
        try:
            inputIpAddress = IPAddress(ipAddress)
        except ValueError:
            logging.error("%s, %s" % (ipAddress, "invalid ip"))
            pass
        # for detail on comparison between IPAddress objects, see Python netaddr module.
        for obj in objs:
            try:
                start = IPAddress(obj.start)
            except ValueError:
                logging.error("%s, %s" % (obj.start, "invalid start ip"))
                pass
            try:
                end = IPAddress(obj.end)
            except ValueError:
                logging.error("%s, %s" % (obj.end, "invalid end ip"))
                pass
            
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
