# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loggingapp', '0002_remove_sessions_sessionend'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sessions',
            old_name='sessionStart',
            new_name='sessionDateTime',
        ),
    ]
