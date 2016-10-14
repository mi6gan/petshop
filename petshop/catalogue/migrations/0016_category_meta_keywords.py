# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0015_auto_20161013_2352'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='meta_keywords',
            field=models.TextField(max_length=100, null=True, blank=True),
        ),
    ]
