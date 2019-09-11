# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0014_add_label_field_to_party'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iprange',
            name='label',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
    ]
