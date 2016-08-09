# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0014_Partner_activationemail_addColumn_PW346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partner',
            name='activationEmailInstructionText',
            field=models.CharField(max_length=9000, null=True),
        ),
    ]
