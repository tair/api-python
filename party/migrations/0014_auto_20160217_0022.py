# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0013_auto_20160217_0017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='affiliation',
            name='consortiumId',
            field=models.ForeignKey(related_name='consortiumId', db_column=b'parentPartyId', to='party.Party'),
        ),
        migrations.AlterField(
            model_name='affiliation',
            name='institutionId',
            field=models.ForeignKey(related_name='institutionId', db_column=b'childPartyId', to='party.Party'),
        ),
    ]
