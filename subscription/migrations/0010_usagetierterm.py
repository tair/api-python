# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0009_usageunitpurchase_transactionid'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsageTierPurchase',
            fields=[
                ('purchaseId', models.AutoField(serialize=False, primary_key=True)),
                ('purchaseDate', models.DateTimeField(default=datetime.datetime.now)),
                ('transactionId', models.CharField(max_length=64, unique=True, null=True)),
                ('syncedToPartner', models.BooleanField(default=False)),
                ('partnerId', models.ForeignKey(to='partner.Partner', db_column=b'partnerId')),
                ('partyId', models.ForeignKey(to='party.Party', db_column=b'partyId')),
            ],
            options={
                'db_table': 'UsageTierPurchase',
            },
        ),
        migrations.CreateModel(
            name='UsageTierTerm',
            fields=[
                ('tierId', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('price', models.IntegerField()),
                ('description', models.CharField(max_length=200)),
                ('isAcademic', models.BooleanField(default=False)),
                ('partnerId', models.ForeignKey(to='partner.Partner', db_column=b'partnerId')),
            ],
            options={
                'db_table': 'UsageTierTerm',
            },
        ),
        migrations.AddField(
            model_name='usagetierpurchase',
            name='tierId',
            field=models.ForeignKey(to='subscription.UsageTierTerm', db_column=b'tierId'),
        ),
    ]
