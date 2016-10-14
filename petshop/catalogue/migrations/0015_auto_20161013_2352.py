# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0014_category_meta_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='page_title',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='meta_description',
            field=models.TextField(max_length=100, null=True, blank=True),
        ),
    ]
