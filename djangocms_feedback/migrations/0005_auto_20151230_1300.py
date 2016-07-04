# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_feedback', '0004_auto_20150626_2002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedbackformpluginmodel',
            name='feedback_type',
            field=models.PositiveIntegerField(null=True, verbose_name='\u0442\u0438\u043f', choices=[(0, b'Generic feedback form')]),
        ),
    ]
