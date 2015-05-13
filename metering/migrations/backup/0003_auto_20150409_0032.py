#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.


# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metering', '0002_limits'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ipAddr',
        ),
        migrations.DeleteModel(
            name='limits',
        ),
    ]
