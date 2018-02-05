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


class AggregationCenterProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AggregationCenterProduct
        fields = ('aggregation_center', 'product', 'active')


class CrateTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CrateType
        fields = ('name', 'weight')


class CrateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Crate
        fields = ('number', 'type')
