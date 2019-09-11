# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0003_subscriptionrequestmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionrequest',
            name='requestType',
            field=models.CharField(default='', max_length=32),
            preserve_default=False,
        ),
    ]
