# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loggingapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='ipsessionaffiliation',
            table='IpSessionAffiliation',
        ),
        migrations.AlterModelTable(
            name='iptableforlogging',
            table='IpTableForLogging',
        ),
        migrations.AlterModelTable(
            name='pageviews2',
            table='PageViews',
        ),
        migrations.AlterModelTable(
            name='partysessionaffiliation',
            table='PartySessionAffiliation',
        ),
        migrations.AlterModelTable(
            name='sessions2',
            table='Sessions',
        ),
    ]
