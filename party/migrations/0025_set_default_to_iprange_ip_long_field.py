# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from common.common import ip2long

def set_ip_long(apps, schema_editor):
    IpRange = apps.get_model('party', 'IpRange')
    for row in IpRange.objects.all():
        row.startLong = ip2long(row.start)
        row.endLong = ip2long(row.end)
        row.save()

class Migration(migrations.Migration):

    dependencies = [
        ('party', '0024_add_ip_long_field_to_iprange'),
    ]

    operations = [
        migrations.RunPython(set_ip_long, reverse_code=migrations.RunPython.noop),
    ]
