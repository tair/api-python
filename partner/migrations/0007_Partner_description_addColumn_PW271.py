# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0006_HomePageUri'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='description',
            field=models.CharField(max_length=300, null=True),
        ),
    ]
