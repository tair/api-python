# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0013_rename_primary_key_partyaffiliation'),
    ]

    operations = [
        migrations.AddField(
            model_name='party',
            name='label',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
