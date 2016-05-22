# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0003_communicationeventtype_staff'),
    ]

    operations = [
        migrations.AlterField(
            model_name='communicationeventtype',
            name='staff',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Managers', blank=True),
        ),
    ]
