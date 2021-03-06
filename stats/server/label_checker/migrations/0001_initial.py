# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-21 20:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Datasets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dataset_name', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Images',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_name', models.CharField(max_length=500)),
                ('hash_digest', models.CharField(max_length=500)),
                ('dataset_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='label_checker.Datasets')),
            ],
        ),
    ]
