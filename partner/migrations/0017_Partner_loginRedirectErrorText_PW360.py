# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0016_Partner_resetpwdemailbody_column_PW357'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='loginRedirectErrorText',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
