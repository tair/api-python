# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0017_Partner_loginRedirectErrorText_PW360'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='defaultLoginRedirect',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
