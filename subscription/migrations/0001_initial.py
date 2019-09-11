# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0001_initial'),
        ('party', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivationCode',
            fields=[
                ('activationCodeId', models.AutoField(serialize=False, primary_key=True)),
                ('activationCode', models.CharField(unique=True, max_length=200)),
                ('period', models.IntegerField()),
                ('purchaseDate', models.DateTimeField(default='2001-01-01T00:00:00Z')),
                ('partnerId', models.ForeignKey(to='partner.Partner', db_column='partnerId', on_delete=models.PROTECT)),
                ('partyId', models.ForeignKey(to='party.Party', null=True, on_delete=models.PROTECT)),
            ],
            options={
                'db_table': 'ActivationCode',
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('subscriptionId', models.AutoField(serialize=False, primary_key=True)),
                ('startDate', models.DateTimeField(default='2000-01-01T00:00:00Z')),
                ('endDate', models.DateTimeField(default='2012-12-21T00:00:00Z')),
                ('partnerId', models.ForeignKey(db_column='partnerId', to='partner.Partner', null=True, on_delete=models.PROTECT)),
                ('partyId', models.ForeignKey(db_column='partyId', to='party.Party', null=True, on_delete=models.PROTECT)),
            ],
            options={
                'db_table': 'Subscription',
            },
        ),
        migrations.CreateModel(
            name='SubscriptionTransaction',
            fields=[
                ('subscriptionTransactionId', models.AutoField(serialize=False, primary_key=True)),
                ('transactionDate', models.DateTimeField(default='2000-01-01T00:00:00Z')),
                ('startDate', models.DateTimeField(default='2001-01-01T00:00:00Z')),
                ('endDate', models.DateTimeField(default='2020-01-01T00:00:00Z')),
                ('transactionType', models.CharField(max_length=200)),
                ('subscriptionId', models.ForeignKey(to='subscription.Subscription', db_column='subscriptionId', on_delete=models.PROTECT)),
            ],
            options={
                'db_table': 'SubscriptionTransaction',
            },
        ),
    ]
