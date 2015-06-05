#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.


from django.db import models
from django.http import Http404

# Create your models here.

class ApiKey(models.Model):
    apiKeyId = models.AutoField(primary_key=True)
    apiKey = models.CharField(max_length=200, unique=True)

    class Meta:
        db_table = "ApiKey"
