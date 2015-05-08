# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0002_auto_20150507_2245'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SubscriptionIpRange',
            new_name='IpRange',
        ),
        migrations.RenameField(
            model_name='iprange',
            old_name='subscriptionIpRangeId',
            new_name='ipRangeId',
        ),
        migrations.AlterModelTable(
            name='iprange',
            table='IpRange',
        ),
    ]
