# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import filer.fields.file
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_urlconfrevision'),
        ('filer', '0002_auto_20150606_2003'),
        ('catalogue', '0006_auto_20160515_0516'),
    ]

    operations = [
        migrations.CreateModel(
            name='CatalogueLinkPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('url', models.CharField(max_length=255, null=True, verbose_name='url', blank=True)),
                ('mailto', models.EmailField(help_text='An email address has priority over both pages and urls', max_length=254, null=True, verbose_name='mailto', blank=True)),
                ('link_style', models.CharField(default=b' ', max_length=255, verbose_name='link style', choices=[(b' ', b'Default')])),
                ('new_window', models.BooleanField(default=False, help_text='Do you want this link to open a new window?', verbose_name='new window?')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='catalogue category', blank=True, to='catalogue.Category', null=True)),
                ('file', filer.fields.file.FilerFileField(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='filer.File', null=True)),
                ('page_link', cms.models.fields.PageField(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='cms.Page', help_text='A link to a page has priority over urls.', null=True, verbose_name='page')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
