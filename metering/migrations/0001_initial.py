# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IpAddressCount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.GenericIPAddressField(db_index=True)),
                ('count', models.IntegerField(default=1)),
                ('partnerId', models.ForeignKey(to='partner.Partner', db_column='partnerId', on_delete=models.PROTECT)),
            ],
            options={
                'db_table': 'IPAddressCount',
            },
        ),
        migrations.CreateModel(
            name='LimitValue',
            fields=[
                ('limitId', models.AutoField(serialize=False, primary_key=True)),
                ('val', models.IntegerField()),
                ('partnerId', models.ForeignKey(to='partner.Partner', db_column='partnerId', on_delete=models.PROTECT)),
            ],
            options={
                'db_table': 'LimitValue',
            },
        ),
    ]
