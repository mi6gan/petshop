# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_urlconfrevision'),
        ('catalogue', '0008_auto_20160522_1004'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductsCarouselPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('style', models.CharField(default=b'default', max_length=2048, verbose_name='style', choices=[(b'default', 'Default')])),
                ('order_by', models.CharField(blank=True, max_length=256, verbose_name='order by', choices=[(b'date_created', 'Bestselling'), (b'stats__score', 'Recently added')])),
                ('count', models.PositiveIntegerField(verbose_name=b'number of products', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(25)])),
                ('categories', models.ManyToManyField(related_name='_productscarouselplugin_categories_+', verbose_name='categories', to='catalogue.Category', blank=True)),
                ('products', models.ManyToManyField(help_text="If you'll add any product here no automatic list will be generated", related_name='_productscarouselplugin_products_+', verbose_name='exact product list', to='catalogue.Category', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.AlterField(
            model_name='cataloguelinkplugin',
            name='link_style',
            field=models.CharField(default=b'', max_length=255, verbose_name='link style', choices=[(b'', 'Default'), (b'btn btn-primary', 'Button')]),
        ),
    ]
