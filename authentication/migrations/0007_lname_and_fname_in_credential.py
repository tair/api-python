# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_Credential_tbl_drop_name_column_PW-161'),
    ]

    operations = [
        migrations.AddField(
            model_name='credential',
            name='firstName',
            field=models.CharField(max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='credential',
            name='lastName',
            field=models.CharField(max_length=32, null=True),
        ),
    ]
