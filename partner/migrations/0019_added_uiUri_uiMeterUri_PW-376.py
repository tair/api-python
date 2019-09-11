# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0018_added_defaultLoginRedirect_PW-373'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='uiMeterUri',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='partner',
            name='uiUri',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
