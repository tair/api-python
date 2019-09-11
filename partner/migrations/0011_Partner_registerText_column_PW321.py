# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0010_added_subscriptionListDesc_field_to_partner_PW-332'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='registerText',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
