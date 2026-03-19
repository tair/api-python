# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0011_add_duration_to_subscription_tier_20220321'),
    ]

    operations = [
        migrations.AddField(
            model_name='usagetierterm',
            name='label',
            field=models.CharField(default='Pro', max_length=20),
            preserve_default=False,
        ),
    ]
