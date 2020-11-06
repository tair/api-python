# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0008_auto_20160820_1956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credential',
            name='userIdentifier',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
