# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_shippingaddress_middle_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(blank=True, max_length=100, verbose_name='Status', choices=[(b'pending', 'Pending for payment'), (b'checked', 'Checked'), (b'paid', 'Paid'), (b'failed', 'Payment is not submitted')]),
        ),
    ]
