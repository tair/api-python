# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0013_Partner_ForgotUIEmail_body_columns_PW342'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='activationEmailInstructionText',
            field=models.CharField(max_length=9000, null=True),
        ),
    ]
