# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_auto_20150821_2103'),
    ]

    operations = [
        migrations.AddField(
            model_name='credential',
            name='name',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
