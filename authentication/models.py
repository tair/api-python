from django.db import models
from party.models import Party
import base64, hmac, hashlib

# Create your models here.

class UsernamePartyAffiliation(models.Model):
  username = models.CharField(max_length=32, db_index=True)
  password = models.CharField(max_length=32)
  email = models.CharField(max_length=128, null=True)
  organization = models.CharField(max_length=64, null=True)
  partyId = models.ForeignKey(Party)
  
  @staticmethod
  def validate(partyId, secretKey):
    if partyId and secretKey:
      pu = Party.objects.filter(partyId=partyId)
      if pu:
        usu = UsernamePartyAffiliation.objects.filter(partyId_id__in=pu.values('partyId')).first()
        digested = base64.b64encode(hmac.new(str(partyId).encode('ascii'), usu.password.encode('ascii'), hashlib.sha1).digest())
        if digested == secretKey:
          return True
    return False

  class Meta:
    db_table = "UsernamePassword"
    unique_together = ("username",)

class GooglePartyAffiliation(models.Model):
  gmail = models.CharField(max_length=128, db_index=True)
  partyId = models.ForeignKey(Party)
  class Meta:
    db_table = "GoogleEmail"
