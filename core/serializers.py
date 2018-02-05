from rest_framework import serializers
from core import models


class AggregationCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AggregationCenter
        fields = ('name', 'location')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ('name',)
