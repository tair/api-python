#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.


# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ipAddr',
            fields=[
                ('ip', models.CharField(max_length=200, serialize=False, primary_key=True)),
                ('count', models.IntegerField(default=1)),
            ],
            options={
                'db_table': 'IPAddressCount',
            },
        ),
        migrations.CreateModel(
            name='limits',
            fields=[
                ('name', models.CharField(max_length=64, serialize=False, primary_key=True)),
                ('val', models.IntegerField()),
            ],
            options={
                'db_table': 'LimitValue',
            },
        ),
    ]
