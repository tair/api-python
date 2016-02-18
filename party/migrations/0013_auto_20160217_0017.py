# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0012_auto_20160216_2349'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='affiliation',
            table='PartyAffiliation',
        ),
    ]
