# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loggingapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pageview',
            name='ip',
            field=models.GenericIPAddressField(default='123.45.67.8'),
            preserve_default=False,
        ),
    ]
