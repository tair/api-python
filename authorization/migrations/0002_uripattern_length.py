# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authorization', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uripattern',
            name='pattern',
            field=models.CharField(default=b'', max_length=5000),
        ),
    ]
