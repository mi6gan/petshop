# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraddress',
            name='middle_name',
            field=models.CharField(max_length=255, verbose_name='Middle name', blank=True),
        ),
    ]
