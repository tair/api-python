# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0004_auto_20150916_2317'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='party',
            name='consortium',
        ),
    ]
