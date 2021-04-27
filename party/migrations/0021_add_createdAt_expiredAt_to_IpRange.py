# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0020_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='iprange',
            name='createdAt',
            field=models.DateTimeField(default='2015-01-01', auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='iprange',
            name='expiredAt',
            field=models.DateTimeField(null=True),
        ),
    ]
