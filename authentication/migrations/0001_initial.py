# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GooglePartyAffiliation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gmail', models.CharField(max_length=128, db_index=True)),
                ('partyId', models.ForeignKey(to='subscription.Party')),
            ],
        ),
        migrations.CreateModel(
            name='UsernamePartyAffiliation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=32, db_index=True)),
                ('password', models.CharField(max_length=32)),
                ('partyId', models.ForeignKey(to='subscription.Party')),
            ],
            options={
                'db_table': 'UsernamePassword',
            },
        ),
    ]
