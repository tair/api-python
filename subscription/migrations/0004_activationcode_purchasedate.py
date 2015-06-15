# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0003_auto_20150612_0211'),
    ]

    operations = [
        migrations.AddField(
            model_name='activationcode',
            name='purchaseDate',
            field=models.DateTimeField(default=b'2001-01-01T00:00:00Z'),
        ),
    ]
