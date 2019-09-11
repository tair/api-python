# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0015_partner_forgotusernametext'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='resetPasswordEmailBody',
            field=models.CharField(max_length=2000, null=True),
        ),
    ]
