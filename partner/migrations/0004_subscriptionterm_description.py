# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0003_subscriptiondescriptionitem_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionterm',
            name='description',
            field=models.CharField(default='1 Month', max_length=200),
            preserve_default=False,
        ),
    ]
