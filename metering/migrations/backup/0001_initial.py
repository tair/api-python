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
                ('ip', models.TextField(serialize=False, primary_key=True)),
                ('count', models.IntegerField(default=1)),
            ],
            options={
                'db_table': 'IPAddressCount',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='limits',
            fields=[
                ('name', models.TextField(serialize=False, primary_key=True)),
                ('val', models.IntegerField()),
            ],
            options={
                'db_table': 'LimitValue',
            },
            bases=(models.Model,),
        ),
    ]
