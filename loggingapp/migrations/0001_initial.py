# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageView',
            fields=[
                ('pageViewId', models.AutoField(serialize=False, primary_key=True)),
                ('uri', models.CharField(max_length=250)),
                ('pageViewDate', models.DateTimeField(default=datetime.datetime.utcnow)),
                ('sessionId', models.CharField(max_length=250)),
                ('partyId', models.ForeignKey(db_column=b'partyId', to='party.Party', null=True)),
            ],
            options={
                'db_table': 'PageView',
            },
        ),
    ]
