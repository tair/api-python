# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metering', '0002_LimitValue_tbl_add_pattern_column_PW-287'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeterBlacklist',
            fields=[
                ('meterBlackListId', models.AutoField(serialize=False, primary_key=True)),
                ('partnerId', models.CharField(default='', max_length=200)),
                ('pattern', models.CharField(default='', max_length=5000)),
            ],
            options={
                'db_table': 'MeterBlacklist',
            },
        ),
    ]
