# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0011_partner_hosturi'),
    ]

    operations = [
        migrations.RenameField(
            model_name='partnerpattern',
            old_name='pattern',
            new_name='sourceUri',
        ),
        migrations.RemoveField(
            model_name='partner',
            name='hostUri',
        ),
        migrations.AddField(
            model_name='partnerpattern',
            name='targetUri',
            field=models.CharField(default='https://back-prod.arabidopsis.org', max_length=200),
            preserve_default=False,
        ),
    ]
