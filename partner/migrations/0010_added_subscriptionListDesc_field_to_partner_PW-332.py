# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0009_Partner_tbl_rename_colums_PW-336'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='subscriptionListDesc',
            field=models.CharField(max_length=1000, null=True),
        ),
    ]
