# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metering', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ipaddr',
            name='ip',
            field=models.GenericIPAddressField(serialize=False, primary_key=True),
        ),
    ]
