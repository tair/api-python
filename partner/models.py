#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.


from django.db import models
from django.http import Http404

# Create your models here.

class Partner(models.Model):
    partnerId = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=200)
    logoUri = models.CharField(max_length=200)
    homeUri = models.CharField(max_length=200, null=True)
    termOfServiceUri = models.CharField(max_length=200)
    description = models.CharField(max_length=300, null=True)
    loginLink = models.CharField(max_length=200, null=True)
    registerLink = models.CharField(max_length=200, null=True)
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
    description = models.CharField(max_length=200)
    partnerId = models.ForeignKey('partner.Partner', db_column="partnerId")
    period = models.IntegerField()
    price = models.DecimalField(decimal_places=2,max_digits=6)
    groupDiscountPercentage = models.DecimalField(decimal_places=2,max_digits=6)

    class Meta:
        db_table = "SubscriptionTerm"

class SubscriptionDescriptionItem(models.Model):
    subscriptionDescriptionItemId = models.AutoField(primary_key=True)
    subscriptionDescriptionId = models.ForeignKey('SubscriptionDescription', db_column='subscriptionDescriptionId')
    text = models.CharField(max_length=2048)

    class Meta:
        db_table = "SubscriptionDescriptionItem"

class SubscriptionDescription(models.Model):
    subscriptionDescriptionId = models.AutoField(primary_key=True)
    header = models.CharField(max_length=200)
    partnerId = models.ForeignKey('Partner', db_column='partnerId')
    descriptionType = models.CharField(max_length=200, default='Default') # Default, Individual, Institution, Commercial

    class Meta:
        db_table = "SubscriptionDescription"
