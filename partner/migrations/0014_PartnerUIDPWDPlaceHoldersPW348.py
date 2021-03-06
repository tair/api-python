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
        migrations.AddField(
            model_name='partner',
            name='forgotUserNameText',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='partner',
            name='loginPasswordFieldPrompt',
            field=models.CharField(default=b'Password', max_length=20),
        ),
        migrations.AddField(
            model_name='partner',
            name='loginUserNameFieldPrompt',
            field=models.CharField(default=b'Username', max_length=20),
        ),
    ]
