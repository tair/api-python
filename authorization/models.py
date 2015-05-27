from django.db import models
import re
from partner.models import Partner

# Create your models here.

class Status():
    ok = "OK"
    meterWarn = "Warning"
    needLogin = "NeedLogin"
    needSubscription = "NeedSubscription"

class UriPattern(models.Model):
    patternId = models.AutoField(primary_key=True)
    pattern = models.CharField(max_length=200, default='')
    class Meta:
        db_table = "UriPattern"

class AccessRule(models.Model):
    accessRuleId = models.AutoField(primary_key=True)
    patternId = models.ForeignKey('UriPattern')
    accessTypeId = models.ForeignKey('AccessType')
    partnerId = models.ForeignKey('partner.Partner')
    class Meta:
        db_table = "AccessRule"

class AccessType(models.Model):
    accessTypeId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    
    @staticmethod
    def checkHasAccessRule(url, accessTypeName, partnerId):
        accessRules = AccessRule.objects.all().filter(partnerId=partnerId)
        for rule in accessRules:
            pattern = re.compile(rule.patternId.pattern)
            if pattern.search(url) and rule.accessTypeId.name == accessTypeName:
                return True

        # no match url.
        return False

    class Meta:
        db_table = "AccessType"
