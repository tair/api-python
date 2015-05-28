# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('loggingapp', '0005_auto_20150518_1843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pageviews2',
            name='pageViewDateTime',
            field=models.DateTimeField(default=datetime.datetime.utcnow),
        ),
        migrations.AlterField(
            model_name='sessions2',
            name='sessionEndDateTime',
            field=models.DateTimeField(default=datetime.datetime.utcnow),
        ),
        migrations.AlterField(
            model_name='sessions2',
            name='sessionStartDateTime',
            field=models.DateTimeField(default=datetime.datetime.utcnow),
        ),
    ]
