# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0016_auto_20241106_2001'),
    ]

    operations = [
        migrations.AddField(
            model_name='buckettransaction',
            name='orcid_id',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
