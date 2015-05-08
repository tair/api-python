# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0003_auto_20150507_2254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriptionterm',
            name='period',
            field=models.IntegerField(verbose_name=11),
        ),
    ]
