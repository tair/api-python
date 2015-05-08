# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loggingapp', '0004_iptableforlogs_sessionipaffiliation_sessionpartyaffiliation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sessions',
            name='sessionUserId',
        ),
        migrations.RemoveField(
            model_name='sessions',
            name='sessionUserType',
        ),
    ]
