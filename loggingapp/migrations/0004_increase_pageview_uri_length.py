# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loggingapp', '0003_PageView_NullableSessionId'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pageview',
            name='uri',
            field=models.CharField(max_length=2000),
        ),
    ]
