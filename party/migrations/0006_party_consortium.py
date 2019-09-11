# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0005_remove_party_consortium'),
    ]

    operations = [
        migrations.AddField(
            model_name='party',
            name='consortium',
            field=models.ForeignKey(to='party.Party', null=True, on_delete=models.PROTECT),
        ),
    ]
