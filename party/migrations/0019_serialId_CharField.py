# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0018_party_serialid_unique'),
    ]

    operations = [
        migrations.AlterField(
            model_name='party',
            name='serialId',
            field=models.CharField(max_length=16, unique=True, null=True),
        ),
    ]
