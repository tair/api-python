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
    if not (partyId and secretKey and partyId.isdigit()):
      return False
    cred = Credential.objects.filter(partyId_id=partyId).first()
    if cred:
      digested = base64.b64encode(hmac.new(str(partyId).encode('ascii'), cred.password.encode('ascii'), hashlib.sha1).digest())
      if digested == secretKey:
        return True
    try:
      party = Party.objects.get(partyId=partyId)
    except Party.DoesNotExist:
      return False
    consortium_ids = list(party.consortiums.values_list('partyId', flat=True))
    for cred in Credential.objects.filter(partyId_id__in=consortium_ids):
      digested = base64.b64encode(hmac.new(str(cred.partyId_id).encode('ascii'), cred.password.encode('ascii'), hashlib.sha1).digest())
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


class OrcidCreditTracking(models.Model):
    orcid_credit_tracking_id = models.AutoField(primary_key=True)
    orcid_id = models.CharField(max_length=255, unique=True)
    credit_reissue_date = models.DateTimeField(null=True)

    class Meta:
        db_table = 'OrcidCreditTracking'