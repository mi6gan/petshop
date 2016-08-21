# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitemaps', '0002_categorysitemapnode'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='categorysitemapnode',
            options={'verbose_name': 'Catalogue category sitemap options', 'verbose_name_plural': 'Catalogue category sitemap options'},
        ),
        migrations.AlterModelOptions(
            name='pagesitemapnode',
            options={'verbose_name': 'CMS page sitemap options', 'verbose_name_plural': 'CMS page sitemap options'},
        ),
        migrations.AddField(
            model_name='categorysitemapnode',
            name='include',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='pagesitemapnode',
            name='include',
            field=models.BooleanField(default=True),
        ),
    ]
