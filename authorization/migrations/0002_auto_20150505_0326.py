# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0001_initial'),
        ('authorization', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pattern',
            name='partnerId',
        ),
        migrations.AddField(
            model_name='accessrule',
            name='partnerId',
            field=models.ForeignKey(default='tair', to='partner.Partner'),
            preserve_default=False,
        ),
    ]
