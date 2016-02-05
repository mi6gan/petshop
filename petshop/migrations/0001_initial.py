# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('logo', easy_thumbnails.fields.ThumbnailerImageField(upload_to=b'petshop/logo', verbose_name='logo')),
                ('favicon', easy_thumbnails.fields.ThumbnailerImageField(upload_to=b'petshop/favicon', verbose_name='favicon')),
                ('site', models.OneToOneField(related_name='settings', editable=False, to='sites.Site')),
            ],
            options={
                'verbose_name': 'Site settings',
                'verbose_name_plural': 'Site settings',
            },
        ),
    ]
