# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0004_auto_20150508_0310'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionTerm',
            fields=[
                ('subscriptionTermId', models.AutoField(serialize=False, primary_key=True)),
                ('period', models.IntegerField(verbose_name=11)),
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
