# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loggingapp', '0008_add_statuscode_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pageview',
            name='statusCode',
            field=models.SmallIntegerField(null=True),
        ),
    ]
