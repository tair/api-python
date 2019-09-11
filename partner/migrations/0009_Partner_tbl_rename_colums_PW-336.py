# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0008_Partner_tbl_add_login_register_link_colums_PW-336'),
    ]

    operations = [
        migrations.RenameField(
            model_name='partner',
            old_name='loginLink',
            new_name='loginUri',
        ),
        migrations.RenameField(
            model_name='partner',
            old_name='registerLink',
            new_name='registerUri',
        ),
    ]
