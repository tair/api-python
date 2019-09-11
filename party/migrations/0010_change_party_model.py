# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0009_auto_20150924_0050'),
    ]

    operations = [
        migrations.CreateModel(
            name='Affiliation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='party',
            name='consortium',
        ),
        migrations.AlterField(
            model_name='party',
            name='country',
            field=models.ForeignKey(db_column='countryId', to='party.Country', null=True, on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='affiliation',
            name='consortiumId',
            field=models.ForeignKey(related_name='consortiumId', db_column='consortiumId', to='party.Party', on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='affiliation',
            name='institutionId',
            field=models.ForeignKey(related_name='institutionId', db_column='institutionId', to='party.Party', on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='party',
            name='consortiums',
            field=models.ManyToManyField(related_name='Affiliation', through='party.Affiliation', to='party.Party'),
        ),
    ]
