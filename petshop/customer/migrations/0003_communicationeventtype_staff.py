# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('customer', '0002_auto_20160515_0516'),
    ]

    operations = [
        migrations.AddField(
            model_name='communicationeventtype',
            name='staff',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Managers'),
        ),
    ]
