# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def populate_bucket_types(apps, schema_editor):
    BucketType = apps.get_model('partner', 'BucketType')
    Partner = apps.get_model('partner', 'Partner')

    # Assuming partnerId is a unique identifier or foreign key reference, we need to look up the Partner object
    tair_partner = Partner.objects.get(partnerId='tair')

    # Define the records to be inserted
    bucket_types = [
        {'bucketTypeId': 10, 'units': 300, 'price': 400.00, 'partnerId': tair_partner, 'description': '300 Units Bucket', 'discountPercentage': 50},
        {'bucketTypeId': 11, 'units': 600, 'price': 775.00, 'partnerId': tair_partner, 'description': '600 Units Bucket', 'discountPercentage': 0},
        {'bucketTypeId': 12, 'units': 900, 'price': 1125.00, 'partnerId': tair_partner, 'description': '900 Units Bucket', 'discountPercentage': 0},
        {'bucketTypeId': 13, 'units': 1200, 'price': 1450.00, 'partnerId': tair_partner, 'description': '1200 Units Bucket', 'discountPercentage': 0},
    ]

    # Insert each record into the BucketType table
    for bucket_type in bucket_types:
        BucketType.objects.create(**bucket_type)

class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0021_subscriptionterm_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='BucketType',
            fields=[
                ('bucketTypeId', models.AutoField(serialize=False, primary_key=True)),
                ('units', models.IntegerField()),
                ('price', models.DecimalField(max_digits=6, decimal_places=2)),
                ('description', models.CharField(max_length=200)),
                ('discountPercentage', models.IntegerField()),
                ('partnerId', models.ForeignKey(to='partner.Partner', db_column=b'partnerId')),
            ],
            options={
                'db_table': 'BucketType',
            },
        ),
        migrations.RunPython(populate_bucket_types)
    ]
