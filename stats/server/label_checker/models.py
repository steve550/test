# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
import hashlib


class Dataset(models.Model):
    dataset_name = models.CharField(max_length=250)

    def __str__(self):
        return self.dataset_name


class Image(models.Model):
    dataset_name = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    image_name = models.CharField(max_length=500)
    #calculate hash_digest of the file
    hash_digest = models.CharField(max_length=500)

    def __str__(self):
        return self.image_name

class Document(models.Model):
    json_file = models.FileField(upload_to='documents/', default = 'documents/None/No-doc.json')
    #json_file2 = models.FileField(upload_to='documents/2/')

class Polygon(models.Model):
    x = models.BigIntegerField()
    y = models.BigIntegerField()

    def __int__(self):
        return self.x, self.y

class WrongId(models.Model):
    object_id = models.CharField(max_length=500)
    #true_polygon = models.ForeignKey(Polygon, on_delete=models.CASCADE, related_name='+', default=Polygon())
    #predicted_polygon = models.ForeignKey(Polygon, on_delete=models.CASCADE, related_name='+', default=Polygon())
    severity = models.FloatField(default=0)

class MissingObject(models.Model):
    object_id = models.CharField(max_length=500)

class MissingPolygon(models.Model):
    object_id = models.CharField(max_length=500)
    #true_polygon = models.ForeignKey(Polygon, on_delete=models.CASCADE, related_name='+', default=Polygon())
    #predicted_polygon = models.ForeignKey(Polygon, on_delete=models.CASCADE, related_name='+', default=Polygon())
    severity = models.FloatField(default=0)

class LabeledCorrectly(models.Model):
    object_id = models.CharField(max_length=500)
    #true_polygon = models.ForeignKey(Polygon, on_delete=models.CASCADE, related_name='+', default=Polygon())
    #predicted_polygon = models.ForeignKey(Polygon, on_delete=models.CASCADE, related_name='+', default=Polygon())
    severity = models.FloatField(default=0)

"""
#create new dataset
dataset1 = Dataset()

#add new image

dataset1.image_set.create(image_name = 'imageName', hash_digest = 'hxx')
dataset1.save()

#get all images
dataset1.image_set.all()

#count number of images
dataset1.image_set.count()

"""