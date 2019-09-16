# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0015_label_allow_blank-PWL-749'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageInfo',
            fields=[
                ('imageInfoId', models.AutoField(serialize=False, primary_key=True)),
                ('partyId', models.ForeignKey(to='party.Party', db_column='partyId', on_delete=models.PROTECT)),
                ('name', models.CharField(max_length=200)),
                ('imageUrl', models.CharField(max_length=500)),
                ('createdAt', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'db_table': 'ImageInfo',
            },
        ),
    ]
