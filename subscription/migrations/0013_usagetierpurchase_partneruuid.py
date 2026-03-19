# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0012_usagetierterm_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='usagetierpurchase',
            name='partnerUUID',
            field=models.CharField(max_length=64, unique=True, null=True),
        ),
    ]
