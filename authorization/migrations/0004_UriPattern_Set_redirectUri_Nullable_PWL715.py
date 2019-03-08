# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0003_UriPattern_RedirectUri_add_column_PWL715'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uripattern',
            name='redirectUri',
            field=models.CharField(default=None, max_length=500, null=True, blank=True),
        ),
    ]
