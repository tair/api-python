# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loggingapp', '0006_pageview_new_fields_PHX-497'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pageview',
            name='meterStatus',
            field=models.CharField(max_length=1, null=True, choices=[('W', 'Warning'), ('B', 'Block'), ('M', 'Must subscribe'), ('N', 'Not metered')]),
        ),
    ]
