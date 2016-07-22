#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.db import models
from partner.models import Partner

class IpAddressCount(models.Model):
    ip = models.GenericIPAddressField(max_length=200, db_index=True)
    count = models.IntegerField(default=1)
    partnerId = models.ForeignKey(Partner, db_column="partnerId")
    class Meta:
        db_table = "IPAddressCount"
    def __str__(self):
        return self.ip

class LimitValue(models.Model):
    limitId = models.AutoField(primary_key=True)
    val = models.IntegerField()
    partnerId = models.ForeignKey(Partner, db_column="partnerId")
    pattern = models.CharField(max_length=5000, default='')#PW-287 length is 5000 like in UriPattern table
    class Meta:
        db_table = "LimitValue"
    def __str__(self):
        return self.limitId
