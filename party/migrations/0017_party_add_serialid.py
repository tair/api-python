# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0016_create_image_info_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='party',
            name='serialId',
            field=models.IntegerField(null=True),
        ),
    ]
