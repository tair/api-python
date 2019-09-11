# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0007_Partner_description_addColumn_PW271'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='loginLink',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='partner',
            name='registerLink',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
