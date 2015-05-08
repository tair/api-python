# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0003_partnerpattern'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='partnerpattern',
            table='PartnerPattern',
        ),
    ]
