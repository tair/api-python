# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GooglePartyAffiliation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gmail', models.CharField(max_length=128, db_index=True)),
                ('partyId', models.ForeignKey(to='party.Party', on_delete=models.PROTECT)),
            ],
            options={
                'db_table': 'GoogleEmail',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=32, db_index=True)),#PW-215 ?
                ('password', models.CharField(max_length=32)),
                ('email', models.CharField(max_length=128, null=True)),
                ('institution', models.CharField(max_length=64, null=True)),
                ('partyId', models.ForeignKey(to='party.Party', db_column='partyId', on_delete=models.PROTECT)),
            ],
            options={
                'db_table': 'User',
            },
        ),
        migrations.AlterUniqueTogether(
            name='user',
            unique_together=set([('username',)]),#PW-215 ?
        ),
    ]
