# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0014_PartnerUIDPWDPlaceHoldersPW348'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='forgotUserNameText',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
