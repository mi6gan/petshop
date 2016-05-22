# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0010_auto_20160522_1208'),
    ]

    operations = [
        migrations.AddField(
            model_name='productscarouselplugin',
            name='title',
            field=models.CharField(default='Title', max_length=255, verbose_name='title'),
            preserve_default=False,
        ),
    ]
