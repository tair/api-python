# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_auto_20150526_2232'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='usernamepartyaffiliation',
            unique_together=set([('username',)]),
        ),
    ]
