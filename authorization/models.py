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
    pattern = models.CharField(max_length=5000, default='')
    redirectUri = models.CharField(max_length=500, default=None, blank=True, null=True)

    @staticmethod
    def getRedirectUri(url, partnerId):
        if not (url and partnerId):
            return None

        accessRules = AccessRule.objects.all().filter(partnerId=partnerId)
        for rule in accessRules:
            try:
                pattern = re.compile(rule.patternId.pattern)
                isPatternValid = True
            except re.error:
                isPatternValid = False

            if isPatternValid and pattern.search(url):
                return rule.patternId.redirectUri

        return None

    class Meta:
        db_table = "UriPattern"


class AccessRule(models.Model):
    accessRuleId = models.AutoField(primary_key=True)
    patternId = models.ForeignKey('UriPattern', on_delete=models.PROTECT)
    accessTypeId = models.ForeignKey('AccessType', on_delete=models.PROTECT)
    partnerId = models.ForeignKey('partner.Partner', on_delete=models.PROTECT)
    class Meta:
        db_table = "AccessRule"

class AccessType(models.Model):
    accessTypeId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)

    @staticmethod
    def checkHasAccessRule(url, accessTypeName, partnerId):
        if not (url and accessTypeName and partnerId):
            return False

        accessRules = AccessRule.objects.all().filter(partnerId=partnerId)
        for rule in accessRules:
            try:
                pattern = re.compile(rule.patternId.pattern)
                isPatternValid = True
            except re.error:
                isPatternValid = False   
            if isPatternValid and pattern.search(url) and rule.accessTypeId.name == accessTypeName:
                return True
        # no match url.
        return False

    class Meta:
        db_table = "AccessType"