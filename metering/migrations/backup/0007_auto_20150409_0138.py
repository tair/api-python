#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.


# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metering', '0006_ipaddr_limits'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ipaddr',
            name='id',
        ),
        migrations.RemoveField(
            model_name='limits',
            name='id',
        ),
        migrations.AlterField(
            model_name='ipaddr',
            name='ip',
            field=models.TextField(serialize=False, primary_key=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='limits',
            name='name',
            field=models.TextField(serialize=False, primary_key=True),
            preserve_default=True,
        ),
    ]
