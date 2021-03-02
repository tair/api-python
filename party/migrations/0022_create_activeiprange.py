# -*- coding: utf-8 -*-
# install dependency: pip install sqlparse
from __future__ import unicode_literals

from django.db import models, migrations

class Migration(migrations.Migration):

    dependencies = [
        ('party', '0021_add_createdAt_expiredAt_to_IpRange'),
    ]

    operations = [
        migrations.RunSQL('CREATE VIEW ActiveIpRange AS SELECT * FROM IpRange WHERE expiredAt IS NULL')
    ]
