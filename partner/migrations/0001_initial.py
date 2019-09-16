# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('partnerId', models.CharField(max_length=200, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('logoUri', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'Partner',
            },
        ),
        migrations.CreateModel(
            name='PartnerPattern',
            fields=[
                ('partnerPatternId', models.AutoField(serialize=False, primary_key=True)),
                ('sourceUri', models.CharField(max_length=200)),
                ('targetUri', models.CharField(max_length=200)),
                ('partnerId', models.ForeignKey(to='partner.Partner', db_column='partnerId', on_delete=models.PROTECT)),
            ],
            options={
                'db_table': 'PartnerPattern',
            },
        ),
        migrations.CreateModel(
            name='SubscriptionTerm',
            fields=[
                ('subscriptionTermId', models.AutoField(serialize=False, primary_key=True)),
                ('period', models.IntegerField()),
                ('price', models.DecimalField(max_digits=6, decimal_places=2)),
                ('groupDiscountPercentage', models.DecimalField(max_digits=6, decimal_places=2)),
                ('partnerId', models.ForeignKey(to='partner.Partner', db_column='partnerId', on_delete=models.PROTECT)),
            ],
            options={
                'db_table': 'SubscriptionTerm',
            },
        ),
    ]
