# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0006_auto_20150508_0337'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscriptionterm',
            name='autoRenew',
        ),
    ]
