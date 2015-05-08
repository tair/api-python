# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0001_initial'),
        ('subscription', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('subscriptionId', models.AutoField(serialize=False, primary_key=True)),
                ('startDate', models.DateTimeField(default=b'2000-01-01T00:00:00Z')),
                ('endDate', models.DateTimeField(default=b'2012-12-21T00:00:00Z')),
                ('partnerId', models.ForeignKey(db_column=b'partnerId', to='partner.Partner', null=True)),
                ('partyId', models.ForeignKey(db_column=b'partyId', to='subscription.Party', null=True)),
            ],
            options={
                'db_table': 'Subscription',
            },
        ),
        migrations.AddField(
            model_name='subscriptioniprange',
            name='partyId',
            field=models.ForeignKey(db_column=b'partyId', default=1, to='subscription.Party'),
            preserve_default=False,
        ),
    ]
