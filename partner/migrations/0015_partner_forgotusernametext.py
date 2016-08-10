# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0014_Partner_activationemail_addColumn_PW346'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='forgotUserNameText',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
