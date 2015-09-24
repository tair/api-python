# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0003_iprange_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='party',
            name='consortium',
            field=models.ForeignKey(to='party.Party', null=True),
        ),
        migrations.AlterField(
            model_name='party',
            name='country',
            field=models.ForeignKey(db_column=b'countryId', default=10, to='party.Country', null=True),
        ),
    ]
