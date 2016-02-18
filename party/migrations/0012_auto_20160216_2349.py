# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0011_auto_20160216_2322'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='affiliation',
            unique_together=set([('institutionId', 'consortiumId')]),
        ),
    ]
