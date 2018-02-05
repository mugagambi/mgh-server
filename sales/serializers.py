from rest_framework import serializers
from sales import models


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Region
        fields = ('name',)


class CustomerSerializer(serializers.ModelSerializer):
    added_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.Customer
        fields = ('name', 'location', 'country_code', 'phone_number',
                  'region', 'created_at', 'updated_at', 'added_by')


class OrderSerializer(serializers.ModelSerializer):
    received_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.Order
        fields = ('customer', 'received_by', 'date_delivery', 'created_at', 'updated_at')


class OrderProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderProducts
        fields = ('order', 'product', 'grade', 'qty', 'price')
