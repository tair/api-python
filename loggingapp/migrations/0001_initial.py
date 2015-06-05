# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0001_initial'),
        ('partner', '0007_remove_subscriptionterm_autorenew'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageView',
            fields=[
                ('pageViewId', models.AutoField(serialize=False, primary_key=True)),
                ('uri', models.CharField(max_length=250)),
                ('pageViewDate', models.DateTimeField(default=datetime.datetime.utcnow)),
                ('partyId', models.ForeignKey(to='party.Party', db_column=b'partyId')),
            ],
            options={
                'db_table': 'PageView',
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('sessionId', models.AutoField(serialize=False, primary_key=True)),
                ('sessionStartDateTime', models.DateTimeField(default=datetime.datetime.utcnow)),
                ('sessionEndDateTime', models.DateTimeField(default=datetime.datetime.utcnow)),
                ('partnerId', models.ForeignKey(to='partner.Partner', db_column=b'partnerId')),
            ],
            options={
                'db_table': 'Session',
            },
        ),
        migrations.AddField(
            model_name='pageview',
            name='sessionId',
            field=models.ForeignKey(db_column=b'sessionId', to='loggingapp.Session', null=True),
        ),
    ]
