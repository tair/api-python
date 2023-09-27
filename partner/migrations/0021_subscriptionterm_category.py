# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0020_Partner_GuideURI_columns_PW419'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionterm',
            name='category',
            field=models.CharField(default=b'academic', max_length=10, choices=[(b'ACADEMIC', b'academic'), (b'COMMERCIAL', b'commercial')]),
        ),
    ]
