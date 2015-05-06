# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0001_initial'),
        ('subscription', '0002_subscriptionstate'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionterm',
            name='partnerId',
            field=models.ForeignKey(db_column=b'partnerId', default='tair', to='partner.Partner'),
            preserve_default=False,
        ),
    ]
