# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0002_uripattern_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='uripattern',
            name='redirectUri',
            field=models.CharField(default=b'', max_length=500),
        ),
    ]
