# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

# Must match authentication.recovery.LOCK_STRIPES.
LOCK_STRIPES = 64


def create_lock_rows(apps, schema_editor):
    AccountRecoveryLock = apps.get_model('authentication', 'AccountRecoveryLock')
    AccountRecoveryLock.objects.bulk_create(
        [AccountRecoveryLock(stripe=i) for i in range(LOCK_STRIPES)])


def delete_lock_rows(apps, schema_editor):
    AccountRecoveryLock = apps.get_model('authentication', 'AccountRecoveryLock')
    AccountRecoveryLock.objects.all().delete()


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
                ('stripe', models.PositiveSmallIntegerField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'AccountRecoveryLock',
            },
        ),
        migrations.RunPython(create_lock_rows, delete_lock_rows),
    ]
