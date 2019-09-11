# -*- coding: utf-8 -*-


from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0012_create_partyaffiliation'),
    ]

    operations = [
        migrations.RenameField(
            model_name='partyaffiliation',
            old_name='id',
            new_name='partyAffiliationId',
        ),
    ]
