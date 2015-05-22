# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='User',
        ),
        migrations.AddField(
            model_name='usernamepartyaffiliation',
            name='email',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='usernamepartyaffiliation',
            name='organization',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
