# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_auto_20150512_1613'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=32, db_index=True)),
                ('password', models.CharField(max_length=32)),
                ('email', models.CharField(max_length=128, null=True)),
                ('organization', models.CharField(max_length=64, null=True)),
            ],
        ),
    ]
