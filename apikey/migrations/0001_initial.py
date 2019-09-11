# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ApiKey',
            fields=[
                ('apiKeyId', models.AutoField(serialize=False, primary_key=True)),
                ('apiKey', models.CharField(unique=True, max_length=200)),
            ],
            options={
                'db_table': 'ApiKey',
            },
        ),
    ]
