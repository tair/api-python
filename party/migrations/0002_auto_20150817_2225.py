# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('party', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('countryId', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'Country',
            },
        ),
        migrations.AddField(
            model_name='party',
            name='display',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='party',
            name='name',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='party',
            name='country',
            field=models.ForeignKey(db_column='countryId', default=334, to='party.Country', null=True, on_delete=models.PROTECT),
        ),
    ]
