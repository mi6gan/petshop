# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0012_auto_20160522_1350'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cataloguelinkplugin',
            name='link_style',
            field=models.CharField(default=b' ', max_length=255, verbose_name='link style', choices=[(b' ', 'Default'), (b'btn btn-primary', 'Button')]),
        ),
    ]
