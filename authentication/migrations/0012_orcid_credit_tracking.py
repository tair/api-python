# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

import logging

logger = logging.getLogger(__name__)


BACKFILL_SQL = """
INSERT INTO OrcidCreditTracking (orcid_id, credit_reissue_date)
SELECT o.orcid_id, u.free_expiry_date
FROM OrcidCredentials o
JOIN Credential c ON o.CredentialId = c.id
JOIN UserBucketUsage u ON c.partyId = u.partyId_id
WHERE o.orcid_id IS NOT NULL
  AND u.free_expiry_date IS NOT NULL;
"""


def backfill_orcid_credit_tracking(apps, schema_editor):
    """Backfill OrcidCreditTracking from OrcidCredentials + Credential + UserBucketUsage."""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM OrcidCreditTracking')
        if cursor.fetchone()[0] > 0:
            logger.info('OrcidCreditTracking already has rows, skipping backfill.')
            return
        cursor.execute(BACKFILL_SQL)
        logger.info('Backfilled %d rows into OrcidCreditTracking.', cursor.rowcount)


def reverse_backfill(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('DELETE FROM OrcidCreditTracking')


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0011_orcid_table_creation'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrcidCreditTracking',
            fields=[
                ('orcid_credit_tracking_id', models.AutoField(serialize=False, primary_key=True)),
                ('orcid_id', models.CharField(max_length=255, unique=True)),
                ('credit_reissue_date', models.DateTimeField(null=True)),
            ],
            options={
                'db_table': 'OrcidCreditTracking',
            },
        ),
        migrations.RunPython(backfill_orcid_credit_tracking, reverse_backfill),
    ]
