# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loggingapp', '0005_added_3_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='pageview',
            name='meterStatus',
            field=models.CharField(max_length=1, null=True),
        ),
    ]
