# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0023_activeiprange'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='iprange',
            name='endLong',
            field=models.BigIntegerField(default=123),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='iprange',
            name='startLong',
            field=models.BigIntegerField(default=456),
            preserve_default=False,
        ),
        migrations.RunSQL('ALTER VIEW ActiveIpRange AS SELECT * FROM IpRange WHERE expiredAt IS NULL')
    ]
