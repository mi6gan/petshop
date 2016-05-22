# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0009_auto_20160522_1153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productscarouselplugin',
            name='products',
            field=models.ManyToManyField(help_text="If you'll add any product here no automatic list will be generated", related_name='_productscarouselplugin_products_+', verbose_name='exact product list', to='catalogue.Product', blank=True),
        ),
    ]
