# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields

from petshop.payment.providers import providers_pool


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('payment', '0002_auto_20141007_2032'),
    ]

    operations = [
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('code', models.SlugField(max_length=128, editable=False)),
                ('settings', jsonfield.fields.JSONField(null=True, editable=False)),
                ('site', models.ForeignKey(to='sites.Site')),
            ],
        ),
        migrations.AddField(
            model_name='sourcetype',
            name='provider',
            field=models.ForeignKey(related_name='source_types', to='payment.Provider', null=True),
            preserve_default=False,
        ),
    ]
