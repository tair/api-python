# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0004_subscriptionrequest_requesttype'),
    ]

    operations = [
        migrations.AddField(
            model_name='activationcode',
            name='transactionType',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
