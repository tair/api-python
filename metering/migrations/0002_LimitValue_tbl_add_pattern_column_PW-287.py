# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metering', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='limitvalue',
            name='pattern',
            field=models.CharField(default='', max_length=5000),
        ),
    ]
