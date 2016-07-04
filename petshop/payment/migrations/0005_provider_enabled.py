# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_auto_20160201_1753'),
    ]

    operations = [
        migrations.AddField(
            model_name='provider',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
    ]
