from django.db import models
from party.models import Party
from partner.models import Partner
import base64, hmac, hashlib

# Create your models here.

class Credential(models.Model):
  #usernameClean = models.CharField(max_length=32, db_index=True, db_column='username').lower().strip()#PW-215 ?
  # PW-351: expand username/email fields to max email size 254
  username = models.CharField(max_length=254, db_index=True)
  firstName = models.CharField(max_length=32, null=True)
  lastName = models.CharField(max_length=32, null=True)
  password = models.CharField(max_length=64)
  email = models.CharField(max_length=254, null=True)
  institution = models.CharField(max_length=200, null=True)#PW-254
  partyId = models.ForeignKey(Party, db_column='partyId', on_delete=models.PROTECT)
  partnerId = models.ForeignKey(Partner, db_column='partnerId', on_delete=models.PROTECT)
  userIdentifier = models.CharField(max_length=32, null=True)
  #name = models.CharField(max_length=64, null=True) vet PW-161

  @staticmethod
  def validate(partyId, secretKey):
    if partyId and secretKey and partyId.isdigit() and Party.objects.filter(partyId=partyId).exists():
      pu = Party.objects.filter(partyId=partyId)
      if Credential.objects.filter(partyId_id__in=pu.values('partyId')).exists():
        usu = Credential.objects.filter(partyId_id__in=pu.values('partyId')).first()
        digested = Credential.generateSecretKey(partyId, usu.password)
        if digested == secretKey:
          return True
      #TODO: validation still fail
      pu = pu.first().consortiums.all()
      if Credential.objects.filter(partyId_id__in=pu.values('partyId')).exists():
        for usu in Credential.objects.filter(partyId_id__in=pu.values('partyId')):
          digested = Credential.generateSecretKey(usu.partyId, usu.password)
          if digested == secretKey:
            return True
    return False

  @staticmethod
  def generatePasswordHash(password):
    return hashlib.sha1(password.encode()).hexdigest()

  @staticmethod
  def generateSecretKey(partyId, password):
    encoded = base64.b64encode(hmac.new(str(partyId).encode('ascii'), password.encode('ascii'), hashlib.sha1).digest())
    return encoded.decode()

  class Meta:
    db_table = "Credential"
    unique_together = ("username","partnerId")

class GooglePartyAffiliation(models.Model):
  gmail = models.CharField(max_length=128, db_index=True)
  partyId = models.ForeignKey(Party, on_delete=models.PROTECT)
  class Meta:
    db_table = "GoogleEmail"
