# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0002_auto_20150817_2225'),
    ]

    operations = [
        migrations.AddField(
            model_name='iprange',
            name='label',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
