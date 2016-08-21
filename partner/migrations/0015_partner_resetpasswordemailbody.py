# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0014_PartnerUIDPWDPlaceHoldersPW348'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='resetPasswordEmailBody',
            field=models.CharField(max_length=2000, null=True),
        ),
    ]
