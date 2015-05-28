# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0007_remove_subscriptionterm_autorenew'),
        ('loggingapp', '0002_auto_20150518_1736'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessions2',
            name='sessionPartnerId',
            field=models.ForeignKey(default='tair', to='partner.Partner'),
            preserve_default=False,
        ),
    ]
