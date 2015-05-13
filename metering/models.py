#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.db import models
from partner.models import Partner

# Create your models here.
#class PositiveBigIntegerField(models.BigIntegerField):
#    empty_strings_allowed = False
#    description = "Big (8 byte) positive integer"
#
#    def db_type(self, connection):
#        """
#        Returns MySQL-specific column data type. Make additional checks
#        to support other backends.
#        """
#        return 'bigint UNSIGNED'
#    def formfield(self, **kwargs):
#        defaults = {'min_value': 0,
#                    'max_value': BigIntegerField.MAX_BIGINT * 2 - 1}
#        defaults.update(kwargs)
#        return super(PositiveBigIntegerField, self).formfield(**defaults)


class ipAddr(models.Model):
    ip = models.GenericIPAddressField(max_length=200, db_index=True)
    count = models.IntegerField(default=1)
    partner = models.ForeignKey(Partner, db_column="partnerId")
    class Meta:
        db_table = "IPAddressCount"
    def __str__(self):
        return self.ip

class limits(models.Model):
    limitId = models.AutoField(primary_key=True)
    val = models.IntegerField()
    partner = models.ForeignKey(Partner, db_column="partnerId")
    class Meta:
        db_table = "LimitValue"
    def __str__(self):
        return self.name
