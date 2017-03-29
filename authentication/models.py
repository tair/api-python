from django.db import models
from party.models import Party
from partner.models import Partner
import base64, hmac, hashlib
from django.contrib.auth.models import User
from rest_framework_jwt.settings import api_settings

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
  partyId = models.ForeignKey(Party, db_column='partyId')
  partnerId = models.ForeignKey(Partner, db_column='partnerId')
  userIdentifier = models.CharField(max_length=32, null=True)
  #name = models.CharField(max_length=64, null=True) vet PW-161
  user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)

  @staticmethod
  def validate(partyId, token, secretKey):
    #verify jwt token
    if token:
      jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
      jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER

      try:
        payload = jwt_decode_handler(token)
      except Exception:
        return False

      username = jwt_get_username_from_payload(payload)

      if not username:
        return False

    # Make sure user exists
      try:
        user = User.objects.get_by_natural_key(username)
      except User.DoesNotExist:
        return False

      return True
        # verify_json_web_token = VerifyJSONWebToken()
        # serializer = verify_json_web_token.get_serializer(data={'token':token})
        # if serializer.is_valid():
        #     return True
        # return False
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

  class Meta:
    db_table = "Credential"
    unique_together = ("username","partnerId")

class GooglePartyAffiliation(models.Model):
  gmail = models.CharField(max_length=128, db_index=True)
  partyId = models.ForeignKey(Party)
  class Meta:
    db_table = "GoogleEmail"
