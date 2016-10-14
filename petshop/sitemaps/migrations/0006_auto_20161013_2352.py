# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitemaps', '0005_auto_20161013_2213'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customsitemapnode',
            options={'ordering': ['location'], 'verbose_name': 'custom SEO entry', 'verbose_name_plural': 'custom SEO entries'},
        ),
    ]
