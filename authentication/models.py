from django.db import models
from party.models import Party
from partner.models import Partner
import base64, hmac, hashlib

# Create your models here.

class User(models.Model):
  username = models.CharField(max_length=32, db_index=True)
  password = models.CharField(max_length=64)
  email = models.CharField(max_length=128, null=True)
  institution = models.CharField(max_length=64, null=True)
  partyId = models.ForeignKey(Party, db_column='partyId')
  partnerId = models.ForeignKey(Partner, db_column='partnerId')
  userIdentifier = models.CharField(max_length=32, null=True)
  
  @staticmethod
  def validate(partyId, secretKey):
    if partyId and secretKey:
      pu = Party.objects.filter(partyId=partyId)
      if pu:
        usu = User.objects.filter(partyId_id__in=pu.values('partyId')).first()
        if usu:
          digested = base64.b64encode(hmac.new(str(partyId).encode('ascii'), usu.password.encode('ascii'), hashlib.sha1).digest())
          if digested == secretKey:
            return True
    return False

  class Meta:
    db_table = "User"
    unique_together = ("username",)

class GooglePartyAffiliation(models.Model):
  gmail = models.CharField(max_length=128, db_index=True)
  partyId = models.ForeignKey(Party)
  class Meta:
    db_table = "GoogleEmail"
