# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0011_Partner_registerText_column_PW321'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='forgotUserNameEmailSubject',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='partner',
            name='forgotUserNameEmailTo',
            field=models.CharField(max_length=128, null=True),
        ),
    ]
