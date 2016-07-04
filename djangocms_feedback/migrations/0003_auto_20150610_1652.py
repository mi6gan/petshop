# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_feedback', '0002_auto_20150525_2116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedbackformpluginmodel',
            name='feedback_type',
            field=models.PositiveIntegerField(null=True, choices=[(0, 'Contacts feedback'), (1, 'Subscribe to news delivery')]),
            preserve_default=True,
        ),
    ]
