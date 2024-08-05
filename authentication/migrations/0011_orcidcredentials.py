# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

import logging

logger = logging.getLogger(__name__)

def populate_orcid_credentials(apps, schema_editor):
    Credential = apps.get_model('authentication', 'Credential')
    OrcidCredentials = apps.get_model('authentication', 'OrcidCredentials')
    
    batch_size = 1000
    credentials = Credential.objects.all()
    total_credentials = credentials.count()
    logger.info('Total credentials: {}'.format(total_credentials))
    for start in range(0, total_credentials, batch_size):
        end = min(start + batch_size, total_credentials)
        batch = credentials[start:end]
        OrcidCredentials.objects.bulk_create([
            OrcidCredentials(credential=credential) for credential in batch
        ])
        logger.info('Processed {} of {}'.format(end, total_credentials))

def reverse_populate_orcid_credentials(apps, schema_editor):
    OrcidCredentials = apps.get_model('authentication', 'OrcidCredentials')
    OrcidCredentials.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0010_credential_increase_lname_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrcidCredentials',
            fields=[
                ('orcid_credential_id', models.AutoField(serialize=False, primary_key=True)),
                ('orcid_id', models.CharField(max_length=255, unique=True, null=True, blank=True)),
                ('orcid_access_token', models.CharField(max_length=255, null=True, blank=True)),
                ('orcid_refresh_token', models.CharField(max_length=255, null=True, blank=True)),
                ('credential', models.ForeignKey(to='authentication.Credential', db_column=b'CredentialId')),
            ],
            options={
                'db_table': 'OrcidCredentials',
            },
        ),
        migrations.RunPython(populate_orcid_credentials, reverse_populate_orcid_credentials),
    ]