# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0005_partner_termofserviceuri'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='homeUri',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
