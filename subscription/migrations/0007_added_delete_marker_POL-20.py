# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0006_cons_fields_subscription_PWL-579'),
    ]

    operations = [
        migrations.AddField(
            model_name='activationcode',
            name='deleteMarker',
            field=models.BooleanField(default=False),
        ),
    ]
