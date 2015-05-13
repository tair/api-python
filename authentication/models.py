from django.db import models
from subscription.models import Party

# Create your models here.

class UsernamePartyAffiliation(models.Model):
  username = models.CharField(max_length=32, db_index=True)
  password = models.CharField(max_length=32)
  partyId = models.ForeignKey(Party)
  class Meta:
    db_table = "UsernamePassword"

class GooglePartyAffiliation(models.Model):
  gmail = models.CharField(max_length=128, db_index=True)
  partyId = models.ForeignKey(Party)
  class Meta:
    db_table = "GoogleEmail"
