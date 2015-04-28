from django.db import models
import re

# Create your models here.

class Status():
    ok = "OK"
    meterWarn = "Warning"
    needSubscription = "NeedSubscription"

class Pattern(models.Model):
    patternId = models.AutoField(primary_key=True)
    pattern = models.CharField(max_length=200, default='')

    class Meta:
        db_table = "Pattern"

class AccessRule(models.Model):
    accessRuleId = models.AutoField(primary_key=True)
    patternId = models.ForeignKey('Pattern')
    accessTypeId = models.ForeignKey('AccessType')
    class Meta:
        db_table = "AccessRule"

class AccessType(models.Model):
    accessTypeId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    
    @staticmethod
    def getByUrl(url):
        accessRules = AccessRule.objects.all()
        for rule in accessRules:
            pattern = re.compile(rule.patternId.pattern)
            if pattern.match(url):
                return rule.accessTypeId.name

        # no match url, free content by default
        return "Free"

    class Meta:
        db_table = "AccessType"
