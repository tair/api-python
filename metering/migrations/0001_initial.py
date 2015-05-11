# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0007_remove_subscriptionterm_autorenew'),
    ]

    operations = [
        migrations.CreateModel(
            name='ipAddr',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.GenericIPAddressField(db_index=True)),
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
