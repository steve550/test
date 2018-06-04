# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Dataset, Image, Document

# Register your models here.
admin.site.register(Dataset)
admin.site.register(Image)
admin.site.register(Document)
