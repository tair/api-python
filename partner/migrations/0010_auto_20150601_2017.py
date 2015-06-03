# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0009_auto_20150529_1937'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='apikey',
            name='partnerId',
        ),
        migrations.DeleteModel(
            name='ApiKey',
        ),
    ]
