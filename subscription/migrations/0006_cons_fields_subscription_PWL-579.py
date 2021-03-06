# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0014_add_label_field_to_party'),
        ('subscription', '0005_added_transactionType_to_activationCode_PW-438'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='consortiumEndDate',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='subscription',
            name='consortiumId',
            field=models.ForeignKey(to='party.Party', null=True),
        ),
        migrations.AddField(
            model_name='subscription',
            name='consortiumStartDate',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='endDate',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='partyId',
            field=models.ForeignKey(related_name='party_id', db_column=b'partyId', to='party.Party', null=True),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='startDate',
            field=models.DateTimeField(null=True),
        ),
    ]
