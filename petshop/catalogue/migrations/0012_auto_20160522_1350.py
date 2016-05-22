# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0011_productscarouselplugin_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productscarouselplugin',
            name='order_by',
            field=models.CharField(blank=True, max_length=256, verbose_name='order by', choices=[(b'stats__score', 'Bestselling'), (b'-date_created', 'Recently added')]),
        ),
    ]
