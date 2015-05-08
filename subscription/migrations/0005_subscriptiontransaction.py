# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0004_auto_20150507_2311'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionTransaction',
            fields=[
                ('subscriptionTransactionId', models.AutoField(serialize=False, primary_key=True)),
                ('transactionDate', models.DateTimeField(default=b'2000-01-01T00:00:00Z')),
                ('startDate', models.DateTimeField(default=b'2001-01-01T00:00:00Z')),
                ('endDate', models.DateTimeField(default=b'2020-01-01T00:00:00Z')),
                ('transactionType', models.CharField(max_length=200)),
                ('subscriptionId', models.ForeignKey(to='subscription.Subscription')),
            ],
            options={
                'db_table': 'SubscriptionTransaction',
            },
        ),
    ]
