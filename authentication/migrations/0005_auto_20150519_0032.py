# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_auto_20150519_0000'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='usernamepartyaffiliation',
            unique_together=set([('username',)]),
        ),
    ]
