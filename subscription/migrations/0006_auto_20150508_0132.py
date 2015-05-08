# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0005_subscriptiontransaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriptiontransaction',
            name='subscriptionId',
            field=models.ForeignKey(to='subscription.Subscription', db_column=b'subscriptionId'),
        ),
    ]
