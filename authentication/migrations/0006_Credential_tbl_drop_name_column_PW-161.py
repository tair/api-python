# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_Credentials_institution_length_64_200'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='credential',
            name='name',
        ),
    ]
