# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitemaps', '0003_auto_20160821_0638'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categorysitemapnode',
            name='location',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='pagesitemapnode',
            name='location',
            field=models.CharField(max_length=200),
        ),
    ]
