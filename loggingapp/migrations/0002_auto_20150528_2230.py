# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loggingapp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='session',
            old_name='sessionEndDateTime',
            new_name='endDate',
        ),
        migrations.RenameField(
            model_name='session',
            old_name='sessionStartDateTime',
            new_name='startDate',
        ),
    ]
