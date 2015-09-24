# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0008_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='party',
            name='country',
            field=models.ForeignKey(db_column=b'countryId', default=219, to='party.Country', null=True),
        ),
    ]
