#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.





# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metering', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='limits',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('val', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
