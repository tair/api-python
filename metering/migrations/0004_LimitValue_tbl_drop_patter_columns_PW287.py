# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metering', '0003_MeterBlacklist_newTable_PW287'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='limitvalue',
            name='pattern',
        ),
    ]
