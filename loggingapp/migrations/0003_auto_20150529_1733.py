# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loggingapp', '0002_auto_20150528_2230'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='session',
            name='partnerId',
        ),
        migrations.AlterField(
            model_name='pageview',
            name='partyId',
            field=models.ForeignKey(db_column=b'partyId', to='party.Party', null=True),
        ),
        migrations.AlterField(
            model_name='pageview',
            name='sessionId',
            field=models.CharField(default='abcdefg', max_length=250),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Session',
        ),
    ]
