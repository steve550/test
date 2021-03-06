# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-30 23:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('label_checker', '0003_document'),
    ]

    operations = [
        migrations.CreateModel(
            name='LabeledCorrectly',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='MissingObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='MissingPolygon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Polygon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.BigIntegerField()),
                ('y', models.BigIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='WrongId',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.CharField(max_length=500)),
                ('polygon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='label_checker.Polygon')),
            ],
        ),
        migrations.AddField(
            model_name='missingpolygon',
            name='polygon',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='label_checker.Polygon'),
        ),
        migrations.AddField(
            model_name='labeledcorrectly',
            name='polygon',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='label_checker.Polygon'),
        ),
    ]
