# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('authentication', '0009_added_user_onetoone_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credential',
            name='user',
            field=models.OneToOneField(unique=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
