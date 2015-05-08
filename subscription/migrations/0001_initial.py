# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0001_initial'),
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
            name='SubscriptionTransaction',
            fields=[
                ('subscriptionIpRangeId', models.AutoField(serialize=False, primary_key=True)),
                ('start', models.GenericIPAddressField()),
                ('end', models.GenericIPAddressField()),
            ],
            options={
                'db_table': 'SubscriptionTransaction',
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
                ('partnerId', models.ForeignKey(to='partner.Partner', db_column=b'partnerId')),
            ],
            options={
                'db_table': 'SubscriptionTerm',
            },
        ),
    ]
