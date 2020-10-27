# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0020_merge'),
        ('partner', '0020_Partner_GuideURI_columns_PW419'),
        ('subscription', '0007_added_delete_marker_POL-20'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsageUnitPurchase',
            fields=[
                ('purchaseId', models.AutoField(serialize=False, primary_key=True)),
                ('quantity', models.IntegerField()),
                ('purchaseDate', models.DateTimeField()),
                ('syncedToPartner', models.BooleanField(default=False)),
                ('partnerId', models.ForeignKey(to='partner.Partner', db_column=b'partnerId')),
                ('partyId', models.ForeignKey(to='party.Party', db_column=b'partyId')),
            ],
            options={
                'db_table': 'UsageUnitPurchase',
            },
        ),
    ]
