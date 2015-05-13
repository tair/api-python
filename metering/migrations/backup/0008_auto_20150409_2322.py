#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.


# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metering', '0007_auto_20150409_0138'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='ipaddr',
            table='IPAddressCount',
        ),
        migrations.AlterModelTable(
            name='limits',
            table='LimitValue',
        ),
    ]
