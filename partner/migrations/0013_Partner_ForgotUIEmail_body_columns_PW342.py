# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0012_Partner_ForgotUIEmail_columns_PW342'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='forgotUserNameEmailBody',
            field=models.CharField(max_length=1000, null=True),
        ),
    ]
