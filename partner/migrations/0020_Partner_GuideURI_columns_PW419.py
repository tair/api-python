# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0019_added_uiUri_uiMeterUri_PW-376'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='guideUri',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
