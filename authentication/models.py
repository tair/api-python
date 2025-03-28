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
  lastName = models.CharField(max_length=64, null=True) #CIPRES-39
  password = models.CharField(max_length=64)
  email = models.CharField(max_length=254, null=True)
  institution = models.CharField(max_length=200, null=True)#PW-254
  partyId = models.ForeignKey(Party, db_column='partyId')
  partnerId = models.ForeignKey(Partner, db_column='partnerId')
  userIdentifier = models.CharField(max_length=64, null=True)#CIPRES-22
  #name = models.CharField(max_length=64, null=True) vet PW-161

  @staticmethod
  def validate(partyId, secretKey):
    if partyId and secretKey and partyId.isdigit() and Party.objects.filter(partyId=partyId).exists():
      pu = Party.objects.filter(partyId=partyId)
      if Credential.objects.filter(partyId_id__in=pu.values('partyId')).exists():
        usu = Credential.objects.filter(partyId_id__in=pu.values('partyId')).first()
        digested = base64.b64encode(hmac.new(str(partyId).encode('ascii'), usu.password.encode('ascii'), hashlib.sha1).digest())
        if digested == secretKey:
          return True
      #TODO: validation still fail
      pu = pu.first().consortiums.all()
      if Credential.objects.filter(partyId_id__in=pu.values('partyId')).exists():
        for usu in Credential.objects.filter(partyId_id__in=pu.values('partyId')):
          digested = base64.b64encode(hmac.new(str(usu.partyId).encode('ascii'), usu.password.encode('ascii'), hashlib.sha1).digest())
          if digested == secretKey:
            return True
    return False

  @staticmethod
  def getByUsernameAndPartner(username, partnerId):
      return Credential.objects.get(username = username, partnerId = partnerId)

  @staticmethod
  def getFirstByUsernameAndPartner(username, partnerId):
      return Credential.objects.filter(username = username, partnerId = partnerId).first()

  class Meta:
    db_table = "Credential"
    unique_together = ("username","partnerId")

class GooglePartyAffiliation(models.Model):
  gmail = models.CharField(max_length=128, db_index=True)
  partyId = models.ForeignKey(Party)
  class Meta:
    db_table = "GoogleEmail"

# Model for new Orcid Credentials
class OrcidCredentials(models.Model):
    orcid_credential_id = models.AutoField(primary_key=True)
    credential = models.ForeignKey('Credential', on_delete=models.CASCADE, db_column='CredentialId')
    orcid_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    orcid_access_token = models.CharField(max_length=255, null=True, blank=True)
    orcid_refresh_token = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'OrcidCredentials'