# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loggingapp', '0005_auto_20150501_2007'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sessionipaffiliation',
            name='sessionIpAffiliationIpTableForLogsId',
        ),
        migrations.RemoveField(
            model_name='sessionipaffiliation',
            name='sessionIpAffiliationSessionId',
        ),
        migrations.RemoveField(
            model_name='sessionpartyaffiliation',
            name='sessionPartyAffiliationPartyId',
        ),
        migrations.RemoveField(
            model_name='sessionpartyaffiliation',
            name='sessionPartyAffiliationSessionId',
        ),
        migrations.AddField(
            model_name='sessions',
            name='sessionUserId',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sessions',
            name='sessionUserType',
            field=models.CharField(default='PARTY', max_length=10),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='IpTableForLogs',
        ),
        migrations.DeleteModel(
            name='SessionIpAffiliation',
        ),
        migrations.DeleteModel(
            name='SessionPartyAffiliation',
        ),
    ]
