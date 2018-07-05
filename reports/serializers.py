from django.utils.formats import number_format
from rest_framework import serializers


class DailySalesChartSerializer(serializers.Serializer):
    period = serializers.DateField(read_only=True)
    total = serializers.SerializerMethodField('total_number', read_only=True)

    def total_number(self, obj):
        return number_format(obj['total'])

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
