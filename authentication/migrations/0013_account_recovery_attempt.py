# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0012_orcid_credit_tracking'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountRecoveryAttempt',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.CharField(max_length=16)),
                ('keyHash', models.CharField(max_length=40)),
                ('createdAt', models.DateTimeField(db_index=True)),
            ],
            options={
                'db_table': 'AccountRecoveryAttempt',
            },
        ),
        migrations.AlterIndexTogether(
            name='accountrecoveryattempt',
            index_together=set([('action', 'keyHash', 'createdAt')]),
        ),
        migrations.CreateModel(
            name='AccountRecoveryLock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.CharField(max_length=16)),
                ('keyHash', models.CharField(max_length=40)),
                ('lastUsed', models.DateTimeField(db_index=True)),
            ],
            options={
                'db_table': 'AccountRecoveryLock',
            },
        ),
        migrations.AlterUniqueTogether(
            name='accountrecoverylock',
            unique_together=set([('action', 'keyHash')]),
        ),
    ]
