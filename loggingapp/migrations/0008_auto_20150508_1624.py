# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('loggingapp', '0007_auto_20150507_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessions2',
            name='sessionEndDateTime',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 8, 16, 24, 27, 219927)),
        ),
        migrations.AlterField(
            model_name='sessions2',
            name='sessionStartDateTime',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 8, 16, 24, 27, 219897)),
        ),
    ]
