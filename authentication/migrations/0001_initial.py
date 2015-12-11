# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GooglePartyAffiliation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gmail', models.CharField(max_length=128, db_index=True)),
                ('partyId', models.ForeignKey(to='party.Party')),
            ],
            options={
                'db_table': 'GoogleEmail',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=32, db_index=True)),#PW-215 ?
                ('password', models.CharField(max_length=32)),
                ('email', models.CharField(max_length=128, null=True)),
                ('institution', models.CharField(max_length=64, null=True)),
                ('partyId', models.ForeignKey(to='party.Party', db_column=b'partyId')),
            ],
            options={
                'db_table': 'User',
            },
        ),
        migrations.AlterUniqueTogether(
            name='user',
            unique_together=set([('username',)]),#PW-215 ?
        ),
    ]
