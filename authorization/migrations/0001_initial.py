# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessRule',
            fields=[
                ('accessRuleId', models.AutoField(serialize=False, primary_key=True)),
            ],
            options={
                'db_table': 'AccessRule',
            },
        ),
        migrations.CreateModel(
            name='AccessType',
            fields=[
                ('accessTypeId', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'AccessType',
            },
        ),
        migrations.CreateModel(
            name='UriPattern',
            fields=[
                ('patternId', models.AutoField(serialize=False, primary_key=True)),
                ('pattern', models.CharField(default='', max_length=200)),
            ],
            options={
                'db_table': 'UriPattern',
            },
        ),
        migrations.AddField(
            model_name='accessrule',
            name='accessTypeId',
            field=models.ForeignKey(to='authorization.AccessType', on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='accessrule',
            name='partnerId',
            field=models.ForeignKey(to='partner.Partner', on_delete=models.PROTECT),
        ),
        migrations.AddField(
            model_name='accessrule',
            name='patternId',
            field=models.ForeignKey(to='authorization.UriPattern', on_delete=models.PROTECT),
        ),
    ]
