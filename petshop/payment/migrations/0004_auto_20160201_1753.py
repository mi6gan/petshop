# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_auto_20160201_1724'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='provider',
            options={'verbose_name': 'provider', 'verbose_name_plural': 'providers'},
        ),
        migrations.AddField(
            model_name='sourcetype',
            name='icon',
            field=easy_thumbnails.fields.ThumbnailerImageField(upload_to=b'oparts/payment', null=True, verbose_name='icon', blank=True),
        ),
    ]
