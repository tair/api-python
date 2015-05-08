# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0005_subscriptionterm'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriptionterm',
            name='period',
            field=models.IntegerField(),
        ),
    ]
