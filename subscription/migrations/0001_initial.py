# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0001_initial'),
    ]

    operations = [
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
            name='SubscriptionIpRange',
            fields=[
                ('subscriptionIpRangeId', models.AutoField(serialize=False, primary_key=True)),
                ('start', models.GenericIPAddressField()),
                ('end', models.GenericIPAddressField()),
                ('partyId', models.ForeignKey(to='subscription.Party', db_column=b'partyId')),
            ],
            options={
                'db_table': 'SubscriptionIpRange',
            },
        ),
        migrations.CreateModel(
            name='SubscriptionTerm',
            fields=[
                ('subscriptionTermId', models.AutoField(serialize=False, primary_key=True)),
                ('period', models.CharField(max_length=200)),
                ('price', models.DecimalField(max_digits=6, decimal_places=2)),
                ('groupDiscountPercentage', models.DecimalField(max_digits=6, decimal_places=2)),
                ('autoRenew', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'SubscriptionTerm',
            },
        ),
    ]
