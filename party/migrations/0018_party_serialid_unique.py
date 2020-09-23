# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0017_party_add_serialid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='party',
            name='serialId',
            field=models.IntegerField(unique=True, null=True),
        ),
    ]
