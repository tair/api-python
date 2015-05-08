# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loggingapp', '0009_auto_20150508_1642'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessions2',
            name='sessionEndDateTime',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='sessions2',
            name='sessionStartDateTime',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
