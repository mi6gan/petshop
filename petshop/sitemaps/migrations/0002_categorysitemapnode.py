# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from decimal import Decimal
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0013_auto_20160522_1414'),
        ('sitemaps', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategorySitemapNode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('changefreq', models.PositiveIntegerField(default=None, null=True, choices=[(None, b'always'), (1, b'hourly'), (24, b'daily'), (168, b'weekly'), (5040, b'monthly'), (60480, b'yearly'), (0, b'never')])),
                ('lastmod', models.DateTimeField(default=django.utils.timezone.now)),
                ('location', models.URLField()),
                ('priority', models.DecimalField(default=Decimal('0.8'), max_digits=2, decimal_places=1, validators=[django.core.validators.MinValueValidator(Decimal('0.0')), django.core.validators.MaxValueValidator(Decimal('1.0'))])),
                ('category', models.OneToOneField(related_name='sitemap_node', to='catalogue.Category')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Sitemap options',
                'verbose_name_plural': 'Sitemap options',
            },
        ),
    ]
