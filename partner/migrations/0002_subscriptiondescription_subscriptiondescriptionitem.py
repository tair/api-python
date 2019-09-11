# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionDescription',
            fields=[
                ('subscriptionDescriptionId', models.AutoField(serialize=False, primary_key=True)),
                ('header', models.CharField(max_length=200)),
                ('descriptionType', models.CharField(default='Default', max_length=200)),
                ('partnerId', models.ForeignKey(to='partner.Partner', db_column='partnerId', on_delete=models.PROTECT)),
            ],
            options={
                'db_table': 'SubscriptionDescription',
            },
        ),
        migrations.CreateModel(
            name='SubscriptionDescriptionItem',
            fields=[
                ('subscriptionDescriptionItemId', models.AutoField(serialize=False, primary_key=True)),
                ('subscriptionDescriptionId', models.ForeignKey(to='partner.SubscriptionDescription', db_column='subscriptionDescriptionId', on_delete=models.PROTECT)),
            ],
            options={
                'db_table': 'SubscriptionDescriptionItem',
            },
        ),
    ]
