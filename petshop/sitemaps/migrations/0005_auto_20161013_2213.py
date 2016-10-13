# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from decimal import Decimal
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('sitemaps', '0004_auto_20161013_1909'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomSitemapNode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('changefreq', models.PositiveIntegerField(default=None, null=True, choices=[(None, b'always'), (1, b'hourly'), (24, b'daily'), (168, b'weekly'), (5040, b'monthly'), (60480, b'yearly'), (0, b'never')])),
                ('lastmod', models.DateTimeField(default=django.utils.timezone.now)),
                ('location', models.CharField(max_length=200)),
                ('priority', models.DecimalField(default=Decimal('0.8'), max_digits=2, decimal_places=1, validators=[django.core.validators.MinValueValidator(Decimal('0.0')), django.core.validators.MaxValueValidator(Decimal('1.0'))])),
                ('include', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['location'],
                'verbose_name': 'custom node SEO entries',
                'verbose_name_plural': 'custom SEO entries',
            },
        ),
        migrations.AlterModelOptions(
            name='categorysitemapnode',
            options={'verbose_name': 'catalogue category SEO options', 'verbose_name_plural': 'catalogue category SEO options'},
        ),
        migrations.AlterModelOptions(
            name='pagesitemapnode',
            options={'verbose_name': 'CMS page SEO options', 'verbose_name_plural': 'CMS page SEO options'},
        ),
        migrations.AlterField(
            model_name='categorysitemapnode',
            name='category',
            field=models.OneToOneField(related_name='sitemap_node', verbose_name='Category', to='catalogue.Category'),
        ),
        migrations.AlterField(
            model_name='pagesitemapnode',
            name='page',
            field=models.OneToOneField(related_name='sitemap_node', verbose_name='Page', to='cms.Page'),
        ),
    ]
