# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-30 00:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('label_checker', '0002_auto_20171129_2346'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('json_file', models.FileField(upload_to='documents/%Y/%m/%d')),
            ],
        ),
    ]
