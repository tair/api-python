# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0025_set_default_to_iprange_ip_long_field'),
        ('authorization', '0003_UriPattern_RedirectUri_add_column_PWL715'),
        ('subscription', '0014_usageaddonoption_usageaddonpricing_usageaddonpurchase_usageaddonpurchasesync'),
    ]

    operations = [
        migrations.CreateModel(
            name='BucketTransaction',
            fields=[
                ('bucket_transaction_id', models.AutoField(serialize=False, primary_key=True)),
                ('transaction_date', models.DateTimeField()),
                ('bucket_type_id', models.IntegerField()),
                ('activation_code_id', models.IntegerField()),
                ('units_per_bucket', models.IntegerField()),
                ('transaction_type', models.CharField(max_length=200)),
                ('email_buyer', models.CharField(max_length=200)),
                ('institute_buyer', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'BucketTransaction',
            },
        ),
        migrations.CreateModel(
            name='PremiumUsageUnits',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('units_consumed', models.IntegerField()),
                ('pattern_object', models.ForeignKey(to='authorization.UriPattern', db_column=b'patternId')),
            ],
            options={
                'db_table': 'PremiumUsageUnits',
            },
        ),
        migrations.CreateModel(
            name='UserBucketUsage',
            fields=[
                ('user_usage_id', models.AutoField(serialize=False, primary_key=True)),
                ('total_units', models.IntegerField()),
                ('remaining_units', models.IntegerField()),
                ('expiry_date', models.DateTimeField()),
                ('partner_id', models.CharField(max_length=200)),
                ('partyId', models.OneToOneField(related_name='user_bucket_usage', null=True, on_delete=django.db.models.deletion.SET_NULL, db_column=b'partyId_id', to='party.Party')),
            ],
            options={
                'db_table': 'UserBucketUsage',
            },
        ),
    ]
