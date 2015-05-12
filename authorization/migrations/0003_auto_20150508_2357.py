# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0002_auto_20150505_0326'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Pattern',
            new_name='UriPattern',
        ),
        migrations.AlterModelTable(
            name='uripattern',
            table='UriPattern',
        ),
    ]
