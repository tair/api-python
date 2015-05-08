# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ipAddr',
            fields=[
                ('ip', models.GenericIPAddressField(serialize=False, primary_key=True)),
                ('count', models.IntegerField(default=1)),
                ('partner', models.ForeignKey(to='partner.Partner', db_column=b'partnerId')),
            ],
            options={
                'db_table': 'IPAddressCount',
            },
        ),
        migrations.CreateModel(
            name='limits',
            fields=[
                ('limitId', models.AutoField(serialize=False, primary_key=True)),
                ('val', models.IntegerField()),
                ('partner', models.ForeignKey(to='partner.Partner', db_column=b'partnerId')),
            ],
            options={
                'db_table': 'LimitValue',
            },
        ),
    ]
