# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0017_buckettransaction_orcid_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionExpirationNotificationLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('run_date', models.DateTimeField()),
                ('success', models.BooleanField(default=False)),
                ('message', models.CharField(max_length=1000, null=True)),
            ],
            options={
                'db_table': 'SubscriptionExpirationNotificationLog',
            },
        ),
    ]
