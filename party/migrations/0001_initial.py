# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='IpRange',
            fields=[
                ('ipRangeId', models.AutoField(serialize=False, primary_key=True)),
                ('start', models.GenericIPAddressField()),
                ('end', models.GenericIPAddressField()),
            ],
            options={
                'db_table': 'IpRange',
            },
        ),
        migrations.CreateModel(
            name='Party',
            fields=[
                ('partyId', models.AutoField(serialize=False, primary_key=True)),
                ('partyType', models.CharField(default=b'user', max_length=200)),
            ],
            options={
                'db_table': 'Party',
            },
        ),
        migrations.AddField(
            model_name='iprange',
            name='partyId',
            field=models.ForeignKey(to='party.Party', db_column=b'partyId'),
        ),
    ]
