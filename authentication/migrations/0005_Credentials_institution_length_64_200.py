# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_credential_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credential',
            name='institution',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
