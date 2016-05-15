# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_auto_20150113_1629'),
    ]

    operations = [
        migrations.AddField(
            model_name='shippingaddress',
            name='middle_name',
            field=models.CharField(max_length=255, verbose_name='Middle name', blank=True),
        ),
    ]
