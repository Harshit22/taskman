# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-16 15:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskman', '0003_auto_20160115_1930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='deadline',
            field=models.DateField(verbose_name='Deadline'),
        ),
    ]
