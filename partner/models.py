#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.


from django.db import models
from django.http import Http404

# Create your models here.

class Partner(models.Model):
    partnerId = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=200)

    class Meta:
        db_table = "Partner"

class PartnerPattern(models.Model):
    partnerPatternId = models.AutoField(primary_key=True)
    partnerId = models.ForeignKey('Partner', db_column='partnerId')
    sourceUri = models.CharField(max_length=200)
    targetUri = models.CharField(max_length=200)
    
    class Meta:
        db_table = "PartnerPattern"

class SubscriptionTerm(models.Model):
    subscriptionTermId = models.AutoField(primary_key=True)
    partnerId = models.ForeignKey('partner.Partner', db_column="partnerId")
    period = models.IntegerField()
    price = models.DecimalField(decimal_places=2,max_digits=6)
    groupDiscountPercentage = models.DecimalField(decimal_places=2,max_digits=6)

    class Meta:
        db_table = "SubscriptionTerm"
