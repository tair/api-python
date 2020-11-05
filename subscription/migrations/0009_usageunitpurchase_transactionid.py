# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0008_usageunitpurchase'),
    ]

    operations = [
        migrations.AddField(
            model_name='usageunitpurchase',
            name='transactionId',
            field=models.CharField(max_length=64, unique=True, null=True),
        ),
    ]
