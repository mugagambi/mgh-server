from django.utils.formats import number_format
from rest_framework import serializers


class CustomDailySalesChartSerializer(serializers.Serializer):
    period = serializers.DateField(read_only=True)
    customer = serializers.SerializerMethodField('customer_number', read_only=True)
    cash = serializers.DecimalField(decimal_places=2, max_digits=15, read_only=True)

    def customer_number(self, obj):
        return number_format(obj['customer'])

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class DailySalesChartSerializer(serializers.Serializer):
    period = serializers.DateField(read_only=True)
    total = serializers.SerializerMethodField('total_number', read_only=True)

    def total_number(self, obj):
        return number_format(obj['total'])

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
