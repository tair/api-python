# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0020_Partner_GuideURI_columns_PW419'),
        ('party', '0025_set_default_to_iprange_ip_long_field'),
        ('subscription', '0013_usagetierpurchase_partneruuid'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsageAddonOption',
            fields=[
                ('optionId', models.AutoField(serialize=False, primary_key=True)),
                ('partnerUUID', models.CharField(max_length=64)),
                ('quantity', models.IntegerField()),
                ('unit', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=64)),
                ('description', models.CharField(max_length=200)),
                ('durationInDays', models.IntegerField()),
                ('proportional', models.BooleanField(default=True)),
                ('partnerId', models.ForeignKey(to='partner.Partner', db_column=b'partnerId')),
            ],
            options={
                'db_table': 'UsageAddonOption',
            },
        ),
        migrations.CreateModel(
            name='UsageAddonPricing',
            fields=[
                ('pricingId', models.AutoField(serialize=False, primary_key=True)),
                ('price', models.IntegerField()),
                ('priority', models.IntegerField()),
                ('threshold', models.IntegerField()),
                ('optionId', models.ForeignKey(related_name='pricing', db_column=b'optionId', to='subscription.UsageAddonOption')),
            ],
            options={
                'ordering': ['priority'],
                'db_table': 'UsageAddonPricing',
            },
        ),
        migrations.CreateModel(
            name='UsageAddonPurchase',
            fields=[
                ('purchaseId', models.AutoField(serialize=False, primary_key=True)),
                ('partnerSubscriptionUUID', models.CharField(max_length=64)),
                ('optionItemQty', models.IntegerField()),
                ('purchaseDate', models.DateTimeField(default=datetime.datetime.now)),
                ('expirationDate', models.DateTimeField()),
                ('transactionId', models.CharField(max_length=64, unique=True, null=True)),
                ('amountPaid', models.DecimalField(max_digits=10, decimal_places=2)),
                ('optionId', models.ForeignKey(to='subscription.UsageAddonOption', db_column=b'optionId')),
                ('partnerId', models.ForeignKey(to='partner.Partner', db_column=b'partnerId')),
                ('partyId', models.ForeignKey(to='party.Party', db_column=b'partyId')),
            ],
            options={
                'db_table': 'UsageAddonPurchase',
            },
        ),
        migrations.CreateModel(
            name='UsageAddonPurchaseSync',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('partnerUUID', models.CharField(max_length=64)),
                ('purchaseId', models.ForeignKey(to='subscription.UsageAddonPurchase', db_column=b'purchaseId')),
            ],
            options={
                'db_table': 'UsageAddonPurchaseSync',
            },
        ),
    ]
