from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('party', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserBucketUsage',
            fields=[
                ('user_usage_id', models.AutoField(primary_key=True, serialize=False)),
                ('total_units', models.IntegerField()),
                ('remaining_units', models.IntegerField()),
                ('expiry_date', models.DateTimeField()),
                ('partner_id', models.CharField(max_length=200)),
                ('partyId', models.OneToOneField(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='party.Party',
                    db_column='partyId_id',
                    related_name='user_bucket_usage'
                )),
            ],
            options={
                'db_table': 'UserBucketUsage',
            },
        ),
        migrations.CreateModel(
            name='PremiumUsageUnits',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('units_consumed', models.IntegerField()),
                ('url', models.CharField(max_length=255)),
                ('patternId', models.ForeignKey(
                    to='party.UriPattern',
                    on_delete=django.db.models.deletion.CASCADE,
                    db_column='patternId'
                )),
            ],
            options={
                'db_table': 'PremiumUsageUnits',
            },
        ),
        migrations.CreateModel(
            name='BucketTransaction',
            fields=[
                ('bucket_transaction_id', models.AutoField(primary_key=True, serialize=False)),
                ('transaction_date', models.DateTimeField()),
                ('bucket_type_id', models.IntegerField()),
                ('activation_code_id', models.IntegerField()),
                ('units_per_bucket', models.IntegerField()),
                ('transaction_type', models.CharField(max_length=200)),
                ('email_buyer', models.CharField(max_length=200)),
                ('institute_buyer', models.CharField(max_length=200))
            ],
            options={
                'db_table': 'BucketTransaction',
            },
        ),
    ]
