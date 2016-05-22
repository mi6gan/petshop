# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0007_cataloguelinkplugin'),
    ]

    operations = [
        migrations.AddField(
            model_name='cataloguelinkplugin',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='product page', blank=True, to='catalogue.Product', null=True),
        ),
        migrations.AlterField(
            model_name='cataloguelinkplugin',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='catalogue category page', blank=True, to='catalogue.Category', null=True),
        ),
    ]
