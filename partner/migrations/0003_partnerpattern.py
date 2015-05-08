# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0002_remove_partner_accesskey'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartnerPattern',
            fields=[
                ('partnerPatternId', models.AutoField(serialize=False, primary_key=True)),
                ('pattern', models.CharField(max_length=200)),
                ('partnerId', models.ForeignKey(to='partner.Partner', db_column=b'partnerId')),
            ],
        ),
    ]
