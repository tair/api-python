from django.db import models
from party.models import Party
from partner.models import Partner

from django.utils import timezone
import datetime
# Create your models here.

class PageView(models.Model):
  pageViewId = models.AutoField(primary_key=True)
  uri = models.CharField(max_length=2000)
  partyId = models.ForeignKey('party.Party', db_column='partyId', null=True)
  pageViewDate = models.DateTimeField(default=datetime.datetime.utcnow)
  sessionId = models.CharField(max_length=250, null=True)
  ip = models.GenericIPAddressField(max_length=200)
  ipList = models.CharField(max_length=250, null=True)
  partnerId = models.ForeignKey(Partner, db_column='partnerId')
  isPaidContent = models.NullBooleanField()

  class Meta:
    db_table = "PageView"
