# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0022_create_activeiprange'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActiveIpRange',
            fields=[
                ('ipRangeId', models.AutoField(serialize=False, primary_key=True)),
                ('start', models.GenericIPAddressField()),
                ('end', models.GenericIPAddressField()),
                ('label', models.CharField(max_length=64, null=True, blank=True)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('expiredAt', models.DateTimeField(null=True)),
            ],
            options={
                'db_table': 'ActiveIpRange',
                'managed': False,
            },
        ),
    ]
