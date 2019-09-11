# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0004_subscriptionterm_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='termOfServiceUri',
            field=models.CharField(default='http://randomuri.com', max_length=200),
            preserve_default=False,
        ),
    ]
