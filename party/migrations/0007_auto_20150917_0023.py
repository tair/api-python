# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0006_party_consortium'),
    ]

    operations = [
        migrations.AlterField(
            model_name='party',
            name='country',
            field=models.ForeignKey(db_column='countryId', default=219, to='party.Country', null=True, on_delete=models.PROTECT),
        ),
    ]
