# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0001_initial'),
        ('subscription', '0004_activationcode_purchasedate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activationcode',
            name='used',
        ),
        migrations.AddField(
            model_name='activationcode',
            name='partyId',
            field=models.ForeignKey(to='party.Party', null=True),
        ),
    ]
