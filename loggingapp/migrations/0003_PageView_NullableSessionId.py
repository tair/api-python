# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loggingapp', '0002_pageview_ip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pageview',
            name='sessionId',
            field=models.CharField(max_length=250, null=True),
        ),
    ]
