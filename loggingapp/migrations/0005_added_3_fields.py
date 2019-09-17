# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0020_Partner_GuideURI_columns_PW419'),
        ('loggingapp', '0004_increase_pageview_uri_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='pageview',
            name='ipList',
            field=models.CharField(max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='pageview',
            name='isPaidContent',
            field=models.BooleanField(null=True),
        ),
        migrations.AddField(
            model_name='pageview',
            name='partnerId',
            field=models.ForeignKey(db_column='partnerId', to='partner.Partner', null=True, on_delete=models.PROTECT),
        ),
    ]
