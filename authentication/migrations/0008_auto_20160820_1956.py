# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_lname_and_fname_in_credential'),
    ]

    operations = [
        migrations.AlterField(
            model_name='credential',
            name='email',
            field=models.CharField(max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='credential',
            name='username',
            field=models.CharField(max_length=254, db_index=True),
        ),
    ]
