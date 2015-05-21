from django.db import models
from party.models import Party
from django.utils import timezone
import datetime
# Create your models here.

class Sessions2(models.Model):
  sessionId = models.AutoField(primary_key=True)
  sessionStartDateTime = models.DateTimeField(auto_now_add=True)
  sessionEndDateTime = models.DateTimeField(auto_now_add=True)
  #sessionExpiration = models.DateTimeField()
  #sessionUserId = models.IntegerField()
  #sessionUserType = models.CharField(max_length=10)

class PageViews2(models.Model):
  pageViewId = models.AutoField(primary_key=True)
  pageViewURI = models.CharField(max_length=250)
  pageViewDateTime = models.DateTimeField()
  pageViewSession = models.ForeignKey("Sessions2", null=True, db_column="sessionId")

class IpTableForLogging(models.Model):
  ipTableId = models.AutoField(primary_key=True)
  ipTableIp = models.GenericIPAddressField()

class PartySessionAffiliation(models.Model):
  partySessionAffiliationId = models.AutoField(primary_key=True)
  partySessionAffiliationParty = models.ForeignKey(Party, null=False, db_column="partyId")
  partySessionAffiliationSession = models.ForeignKey("Sessions2", null=False, db_column="sessionId")

class IpSessionAffiliation(models.Model):
  ipSessionAffiliationId = models.AutoField(primary_key=True)
  ipSessionAffiliationIp = models.ForeignKey("IpTableForLogging", null=False, db_column="ipTableId")
  ipSessionAffiliationSession = models.ForeignKey("Sessions2", null=False, db_column="sessionId")
 
