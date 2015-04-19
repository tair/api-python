#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.


# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
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
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('paymentId', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'Payment',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('startDate', models.DateTimeField(default=b'2000-01-01T00:00:00Z')),
                ('endDate', models.DateTimeField(default=b'2012-12-21T00:00:00Z')),
                ('partyId', models.ForeignKey(db_column=b'partyId', to='subscription.Party', null=True)),
            ],
            options={
                'db_table': 'Subscription',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubscriptionIpRange',
            fields=[
                ('subscriptionIpRangeId', models.AutoField(serialize=False, primary_key=True)),
                ('start', models.GenericIPAddressField()),
                ('end', models.GenericIPAddressField()),
                ('partyId', models.ForeignKey(to='subscription.Subscription', db_column=b'partyId')),
            ],
            options={
                'db_table': 'SubscriptionIpRange',
            },
            bases=(models.Model,),
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
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='subscription',
            name='subscriptionTermId',
            field=models.ForeignKey(db_column=b'subscriptionTermId', default=1, to='subscription.SubscriptionTerm'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='payment',
            name='partyId',
            field=models.ForeignKey(db_column=b'partyId', to='subscription.Subscription', null=True),
            preserve_default=True,
        ),
    ]
