# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('loggingapp', '0004_auto_20150518_1830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pageviews2',
            name='pageViewDateTime',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
