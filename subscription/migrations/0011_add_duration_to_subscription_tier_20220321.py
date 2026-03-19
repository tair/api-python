# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0010_usagetierterm'),
    ]

    operations = [
        migrations.AddField(
            model_name='usagetierpurchase',
            name='expirationDate',
            field=models.DateTimeField(default='2022-12-31 23:59:59'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usagetierterm',
            name='durationInDays',
            field=models.IntegerField(default=365),
            preserve_default=False,
        ),
    ]
