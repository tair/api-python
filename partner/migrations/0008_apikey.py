# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0007_remove_subscriptionterm_autorenew'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiKey',
            fields=[
                ('apiKeyId', models.AutoField(serialize=False, primary_key=True)),
                ('apiKey', models.CharField(max_length=200)),
                ('partnerId', models.ForeignKey(to='partner.Partner', db_column=b'partnerId')),
            ],
            options={
                'db_table': 'ApiKey',
            },
        ),
    ]
