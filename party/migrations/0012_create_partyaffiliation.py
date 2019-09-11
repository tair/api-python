# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0011_remove_affiliation'),
    ]

    operations = [
        migrations.CreateModel(
            name='PartyAffiliation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('childPartyId', models.ForeignKey(related_name='childPartyId', db_column='childPartyId', to='party.Party', on_delete=models.PROTECT)),
                ('parentPartyId', models.ForeignKey(related_name='parentPartyId', db_column='parentPartyId', to='party.Party', on_delete=models.PROTECT)),
            ],
            options={
                'db_table': 'PartyAffiliation',
            },
        ),
        migrations.AddField(
            model_name='party',
            name='consortiums',
            field=models.ManyToManyField(related_name='PartyAffiliation', through='party.PartyAffiliation', to='party.Party'),
        ),
        migrations.AlterUniqueTogether(
            name='partyaffiliation',
            unique_together=set([('childPartyId', 'parentPartyId')]),
        ),
    ]
