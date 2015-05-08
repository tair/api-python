# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PageViews',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pageViewURI', models.CharField(max_length=250)),
                ('pageViewDateTime', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Sessions',
            fields=[
                ('sessionId', models.AutoField(serialize=False, primary_key=True)),
                ('sessionStart', models.DateTimeField()),
                ('sessionEnd', models.DateTimeField()),
                ('sessionUserId', models.IntegerField()),
                ('sessionUserType', models.CharField(max_length=10)),
            ],
        ),
        migrations.AddField(
            model_name='pageviews',
            name='pageViewSession',
            field=models.ForeignKey(db_column=b'sessionId', to='loggingapp.Sessions', null=True),
        ),
    ]
