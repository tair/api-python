# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0008_apikey'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apikey',
            name='apiKey',
            field=models.CharField(unique=True, max_length=200),
        ),
    ]
