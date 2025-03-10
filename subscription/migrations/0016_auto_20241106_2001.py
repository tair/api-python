# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0015_buckettransaction_premiumusageunits_userbucketusage'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserTrackPages',
            fields=[
                ('userTrackPagesId', models.AutoField(serialize=False, primary_key=True)),
                ('partyId', models.IntegerField()),
                ('uri', models.CharField(max_length=2000)),
                ('timestamp', models.DateTimeField()),
            ],
            options={
                'db_table': 'UserTrackPages',
            },
        ),
        migrations.AddField(
            model_name='userbucketusage',
            name='free_expiry_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='userbucketusage',
            name='expiry_date',
            field=models.DateTimeField(null=True),
        ),
    ]
