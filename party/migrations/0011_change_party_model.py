# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0010_change_party_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='party',
            name='consortiums',
            field=models.ManyToManyField(related_name='Affiliation', through='party.Affiliation', to='party.Party'),
        ),
    ]
