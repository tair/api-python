# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('loggingapp', '0003_sessions2_sessionpartnerid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessions2',
            name='sessionEndDateTime',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='sessions2',
            name='sessionStartDateTime',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
