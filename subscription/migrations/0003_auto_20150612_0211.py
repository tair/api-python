# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0002_activationcode_activationcode'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activationcode',
            name='endDate',
        ),
        migrations.RemoveField(
            model_name='activationcode',
            name='startDate',
        ),
        migrations.AddField(
            model_name='activationcode',
            name='period',
            field=models.IntegerField(default=180),
            preserve_default=False,
        ),
    ]
