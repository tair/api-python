# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loggingapp', '0007_choices_meterstatus_PHX-497'),
    ]

    operations = [
        migrations.AddField(
            model_name='pageview',
            name='statusCode',
            field=models.IntegerField(null=True),
        ),
    ]
