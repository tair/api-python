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
            field=models.CharField(max_length=1, null=True, choices=[(b'W', b'Warning'), (b'B', b'Block'), (b'M', b'Must subscribe'), (b'N', b'Not metered')]),
        ),
    ]
