# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0003_iprange_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='party',
            name='consortium',
            field=models.ForeignKey(to='party.Party', null=True, on_delete=models.PROTECT),
        ),
        migrations.AlterField(
            model_name='party',
            name='country',
            field=models.ForeignKey(db_column='countryId', default=10, to='party.Country', null=True, on_delete=models.PROTECT),
        ),
    ]
