# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0006_auto_20150508_0337'),
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
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('subscriptionId', models.AutoField(serialize=False, primary_key=True)),
                ('startDate', models.DateTimeField(default=b'2000-01-01T00:00:00Z')),
                ('endDate', models.DateTimeField(default=b'2012-12-21T00:00:00Z')),
                ('partnerId', models.ForeignKey(db_column=b'partnerId', to='partner.Partner', null=True)),
                ('partyId', models.ForeignKey(db_column=b'partyId', to='subscription.Party', null=True)),
            ],
            options={
                'db_table': 'Subscription',
            },
        ),
        migrations.CreateModel(
            name='SubscriptionTransaction',
            fields=[
                ('subscriptionTransactionId', models.AutoField(serialize=False, primary_key=True)),
                ('transactionDate', models.DateTimeField(default=b'2000-01-01T00:00:00Z')),
                ('startDate', models.DateTimeField(default=b'2001-01-01T00:00:00Z')),
                ('endDate', models.DateTimeField(default=b'2020-01-01T00:00:00Z')),
                ('transactionType', models.CharField(max_length=200)),
                ('subscriptionId', models.ForeignKey(to='subscription.Subscription', db_column=b'subscriptionId')),
            ],
            options={
                'db_table': 'SubscriptionTransaction',
            },
        ),
        migrations.AddField(
            model_name='iprange',
            name='partyId',
            field=models.ForeignKey(to='subscription.Party', db_column=b'partyId'),
        ),
    ]
