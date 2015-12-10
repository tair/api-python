# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0011_change_party_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='affiliation',
            name='consortiumId',
            field=models.ForeignKey(related_name='consortiumId', db_column=b'consortiumId', to='party.Party'),
        ),
        migrations.AlterField(
            model_name='affiliation',
            name='institutionId',
            field=models.ForeignKey(related_name='institutionId', db_column=b'institutionId', to='party.Party'),
        ),
    ]
