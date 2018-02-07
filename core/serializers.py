from rest_framework import serializers
from core import models


class AggregationCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AggregationCenter
        fields = ('id', 'name', 'location')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ('id', 'name',)


class AggregationCenterProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AggregationCenterProduct
        fields = ('id', 'aggregation_center', 'product', 'active')


class CrateTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CrateType
        fields = ('id', 'name', 'weight')


class CrateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Crate
        fields = ('id', 'number', 'type')


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Grade
        fields = ('id', 'name',)
