# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IpSessionAffiliation',
            fields=[
                ('ipSessionAffiliationId', models.AutoField(serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='IpTableForLogging',
            fields=[
                ('ipTableId', models.AutoField(serialize=False, primary_key=True)),
                ('ipTableIp', models.GenericIPAddressField()),
            ],
        ),
        migrations.CreateModel(
            name='PageViews2',
            fields=[
                ('pageViewId', models.AutoField(serialize=False, primary_key=True)),
                ('pageViewURI', models.CharField(max_length=250)),
                ('pageViewDateTime', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='PartySessionAffiliation',
            fields=[
                ('partySessionAffiliationId', models.AutoField(serialize=False, primary_key=True)),
                ('partySessionAffiliationParty', models.ForeignKey(to='subscription.Party', db_column=b'partyId')),
            ],
        ),
        migrations.CreateModel(
            name='Sessions2',
            fields=[
                ('sessionId', models.AutoField(serialize=False, primary_key=True)),
                ('sessionStartDateTime', models.DateTimeField(auto_now_add=True)),
                ('sessionEndDateTime', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='partysessionaffiliation',
            name='partySessionAffiliationSession',
            field=models.ForeignKey(to='loggingapp.Sessions2', db_column=b'sessionId'),
        ),
        migrations.AddField(
            model_name='pageviews2',
            name='pageViewSession',
            field=models.ForeignKey(db_column=b'sessionId', to='loggingapp.Sessions2', null=True),
        ),
        migrations.AddField(
            model_name='ipsessionaffiliation',
            name='ipSessionAffiliationIp',
            field=models.ForeignKey(to='loggingapp.IpTableForLogging', db_column=b'ipTableId'),
        ),
        migrations.AddField(
            model_name='ipsessionaffiliation',
            name='ipSessionAffiliationSession',
            field=models.ForeignKey(to='loggingapp.Sessions2', db_column=b'sessionId'),
        ),
    ]
