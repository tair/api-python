# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0012_create_partyaffiliation'),
    ]

    operations = [
        migrations.RenameField(
            model_name='partyaffiliation',
            old_name='id',
            new_name='partyAffiliationId',
        ),
    ]
