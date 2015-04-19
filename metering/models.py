#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.





from django.db import models

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
    ip = models.CharField(max_length=200, primary_key=True)
    count = models.IntegerField(default=1)
    class Meta:
        db_table = "IPAddressCount"
    def __str__(self):
        return self.ip

class limits(models.Model):
    name = models.CharField(max_length=64, primary_key=True)
    val = models.IntegerField()
    class Meta:
        db_table = "LimitValue"
    def __str__(self):
        return self.name
