from django.db import models
from party.models import Party
from partner.models import Partner

from django.utils import timezone
import datetime
# Create your models here.

class PageView(models.Model):
  pageViewId = models.AutoField(primary_key=True)
  uri = models.CharField(max_length=2000)
  partyId = models.ForeignKey('party.Party', db_column='partyId', null=True, on_delete=models.PROTECT)
  pageViewDate = models.DateTimeField(default=datetime.datetime.utcnow)
  sessionId = models.CharField(max_length=250, null=True)
  ip = models.GenericIPAddressField(max_length=200)
  ipList = models.CharField(max_length=250, null=True)
  partnerId = models.ForeignKey(Partner, db_column='partnerId', null=True, on_delete=models.PROTECT)
  isPaidContent = models.BooleanField(null=True)

  # meter choices
  METER_WARNING_STATUS = 'W'
  METER_BLOCK_STATUS = 'B'
  METER_MUST_SUBSCRIBE_STATUS = 'M'
  METER_NOT_METERED_STATUS = 'N'
  METER_STATUS_CHOICES = (
    (METER_WARNING_STATUS, 'Warning'),
    (METER_BLOCK_STATUS, 'Block'),
    (METER_MUST_SUBSCRIBE_STATUS, 'Must subscribe'),
    (METER_NOT_METERED_STATUS, 'Not metered'),
  )
  meterStatus = models.CharField(max_length=1, choices=METER_STATUS_CHOICES, null=True)

  class Meta:
    db_table = "PageView"
