#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.


from django.db import models
from django.http import Http404

# Create your models here.

class Partner(models.Model):
    partnerId = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=200)

    @staticmethod
    def validatePartnerId(serializerObj, savePartnerId):
        request = serializerObj.context['view'].request
        queryPartnerId = request.GET.get('partnerId')
        if not queryPartnerId == savePartnerId:
            raise Http404

    @staticmethod
    def getQuerySet(view, model, modelPartnerId):
        return Partner.filters(view, model.objects.all(), modelPartnerId)

    @staticmethod
    def getPartnerId(view):
        return view.request.GET.get('partnerId')

    @staticmethod
    def filters(view, obj, modelPartnerId):
        # TODO, add security handling here. (e.g. gets accessKey and translate to partnerId)
        partnerId = Partner.getPartnerId(view)
        filters = {modelPartnerId:partnerId}
        if partnerId == None:
            return []
        return obj.filter(**filters)

    class Meta:
        db_table = "Partner"

class PartnerPattern(models.Model):
    partnerPatternId = models.AutoField(primary_key=True)
    partnerId = models.ForeignKey('Partner', db_column='partnerId')
    pattern = models.CharField(max_length=200)
    
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
