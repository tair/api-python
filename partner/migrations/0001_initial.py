# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('partnerId', models.CharField(max_length=200, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('accessKey', models.CharField(unique=True, max_length=200)),
            ],
            options={
                'db_table': 'Partner',
            },
        ),
    ]
