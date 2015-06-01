# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metering', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ipAddr',
            new_name='IpAddressCount',
        ),
        migrations.RenameModel(
            old_name='limits',
            new_name='LimitValue',
        ),
        migrations.RenameField(
            model_name='ipaddresscount',
            old_name='partner',
            new_name='partnerId',
        ),
        migrations.RenameField(
            model_name='limitvalue',
            old_name='partner',
            new_name='partnerId',
        ),
    ]
