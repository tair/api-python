# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0016_create_image_info_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='abbreviation',
            field=models.CharField(default='', max_length=2),
            preserve_default=False,
        ),
    ]
