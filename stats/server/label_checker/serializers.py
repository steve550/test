from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from .models import WrongId, MissingPolygon, MissingObject, LabeledCorrectly

class WrongIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = WrongId
        fields = '__all__'

class MissingObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissingObject
        fields = '__all__'

class MissingPolygonSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissingPolygon
        fields = '__all__'

class LabeledCorrectlySerializer(serializers.ModelSerializer):
    class Meta:
        model = LabeledCorrectly
        fields = '__all__'


