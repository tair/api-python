# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0002_subscriptiondescription_subscriptiondescriptionitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptiondescriptionitem',
            name='text',
            field=models.CharField(default='you get 5% discount for every purchase', max_length=2048),
            preserve_default=False,
        ),
    ]
