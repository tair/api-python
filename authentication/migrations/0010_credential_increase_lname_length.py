# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0009_auto_20200721_2147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credential',
            name='lastName',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
