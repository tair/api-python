# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0005_partner_termofserviceuri'),
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='partnerId',
            field=models.ForeignKey(db_column=b'partnerId', default='test', to='partner.Partner'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='userIdentifier',
            field=models.CharField(max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterUniqueTogether(
            name='user',
            unique_together=set([('username', 'partnerId')]),
        ),
    ]
