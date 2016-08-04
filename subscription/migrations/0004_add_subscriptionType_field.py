# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0003_subscriptionrequestmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionrequest',
            name='requestType',
            field=models.CharField(default='request', max_length=32),
            preserve_default=False,
        ),
    ]
