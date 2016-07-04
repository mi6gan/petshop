# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_feedback', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedbackformpluginmodel',
            name='feedback_type',
            field=models.PositiveIntegerField(null=True, choices=[(0, 'Name and phone'), (1, 'On timer popup feedback form')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='feedbackformpluginmodel',
            name='title',
            field=models.CharField(max_length=128, null=True, verbose_name='\u0437\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a', blank=True),
            preserve_default=True,
        ),
    ]
