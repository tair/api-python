# -*- coding: utf-8 -*-


from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0011_Partner_registerText_column_PW321'),
        ('subscription', '0002_unique_constraint_partyId_partnerId'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionRequest',
            fields=[
                ('subscriptionRequestId', models.AutoField(serialize=False, primary_key=True)),
                ('requestDate', models.DateTimeField(default=datetime.datetime.now)),
                ('firstName', models.CharField(max_length=32)),
                ('lastName', models.CharField(max_length=32)),
                ('email', models.CharField(max_length=128)),
                ('institution', models.CharField(max_length=200)),
                ('librarianName', models.CharField(max_length=100)),
                ('librarianEmail', models.CharField(max_length=128)),
                ('comments', models.CharField(max_length=5000)),
                ('partnerId', models.ForeignKey(db_column='partnerId', to='partner.Partner', max_length=200, on_delete=models.PROTECT)),
            ],
            options={
                'db_table': 'SubscriptionRequest',
            },
        ),
    ]
