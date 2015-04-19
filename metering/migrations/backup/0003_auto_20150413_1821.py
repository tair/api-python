#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.


# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metering', '0002_auto_20150410_1928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ipaddr',
            name='ip',
            field=models.CharField(max_length=200, serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='limits',
            name='name',
            field=models.CharField(max_length=64, serialize=False, primary_key=True),
        ),
    ]
