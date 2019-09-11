# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0010_change_party_model'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='affiliation',
            name='consortiumId',
        ),
        migrations.RemoveField(
            model_name='affiliation',
            name='institutionId',
        ),
        migrations.RemoveField(
            model_name='party',
            name='consortiums',
        ),
        migrations.DeleteModel(
            name='Affiliation',
        ),
    ]
