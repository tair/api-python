from django.db import models
import re
from partner.models import Partner

import logging
logger = logging.getLogger('phoenix.api.authorization')
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
    patternId = models.ForeignKey('UriPattern')
    accessTypeId = models.ForeignKey('AccessType')
    partnerId = models.ForeignKey('partner.Partner')
    class Meta:
        db_table = "AccessRule"

class AccessType(models.Model):
    accessTypeId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)

    @staticmethod
    def getMatchingRules(url, partnerId):
        """
        Load all access rules for partner once with select_related, evaluate regex,
        return Login/Paid/redirectUri in a single pass. Use this instead of
        calling checkHasAccessRule multiple times.
        """
        if not (url and partnerId):
            return {"Login": False, "Paid": False, "redirectUri": None}

        accessRules = AccessRule.objects.filter(partnerId=partnerId).select_related(
            'patternId', 'accessTypeId'
        )
        result = {"Login": False, "Paid": False, "redirectUri": None}
        for rule in accessRules:
            try:
                pattern = re.compile(rule.patternId.pattern)
                isPatternValid = True
            except re.error:
                logger.info("Error compiling pattern: %s" % rule.patternId.pattern)
                isPatternValid = False
            if not isPatternValid:
                continue
            if not pattern.search(url):
                continue
            access_type_name = rule.accessTypeId.name
            if access_type_name == "Login":
                result["Login"] = True
            elif access_type_name == "Paid":
                result["Paid"] = True
            if result["redirectUri"] is None:
                result["redirectUri"] = rule.patternId.redirectUri
        return result

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
                logger.info("Error compiling pattern: %s" % rule.patternId.pattern)
                isPatternValid = True
            if isPatternValid and pattern.search(url) and rule.accessTypeId.name == accessTypeName:
                return True
        # no match url.
        return False

    class Meta:
        db_table = "AccessType"