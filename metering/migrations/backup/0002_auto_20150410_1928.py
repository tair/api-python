#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.


# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metering', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ipaddr',
            name='count',
            field=models.IntegerField(default=1),
            preserve_default=True,
        ),
    ]
