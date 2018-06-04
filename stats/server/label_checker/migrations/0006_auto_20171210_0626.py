# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('label_checker', '0005_auto_20171201_2336'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='labeledcorrectly',
            name='polygon',
        ),
        migrations.RemoveField(
            model_name='missingpolygon',
            name='polygon',
        ),
        migrations.RemoveField(
            model_name='wrongid',
            name='polygon',
        ),
        migrations.AddField(
            model_name='labeledcorrectly',
            name='severity',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='missingpolygon',
            name='severity',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='wrongid',
            name='severity',
            field=models.FloatField(default=0),
        ),
    ]
