# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0001_initial'),
        ('loggingapp', '0003_auto_20150429_2305'),
    ]

    operations = [
        migrations.CreateModel(
            name='IpTableForLogs',
            fields=[
                ('ipTableForLogsId', models.AutoField(serialize=False, primary_key=True)),
                ('ipTableForLogsIp', models.GenericIPAddressField()),
            ],
        ),
        migrations.CreateModel(
            name='SessionIpAffiliation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sessionIpAffiliationIpTableForLogsId', models.ForeignKey(to='loggingapp.IpTableForLogs', db_column=b'ipTableForLogsId')),
                ('sessionIpAffiliationSessionId', models.ForeignKey(to='loggingapp.Sessions', db_column=b'sessionId')),
            ],
        ),
        migrations.CreateModel(
            name='SessionPartyAffiliation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sessionPartyAffiliationPartyId', models.ForeignKey(to='subscription.Party', db_column=b'partyId')),
                ('sessionPartyAffiliationSessionId', models.ForeignKey(to='loggingapp.Sessions', db_column=b'sessionId')),
            ],
        ),
    ]
