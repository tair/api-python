# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0010_auto_20150601_2017'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='hostUri',
            field=models.CharField(default='http://back-prod.arabidopsis.org', max_length=200),
            preserve_default=False,
        ),
    ]
