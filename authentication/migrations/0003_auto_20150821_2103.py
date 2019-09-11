# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_auto_20150806_1926'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='User',
            new_name='Credential',
        ),
        migrations.AlterModelTable(
            name='credential',
            table='Credential',
        ),
    ]
