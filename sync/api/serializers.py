from rest_framework import serializers


class DataSerializer(serializers.Serializer):
    customers = serializers.ListField(required=True)
    orders = serializers.ListField(required=True)
    order_products = serializers.ListField(required=True)
    packages = serializers.ListField(required=True)
    package_products = serializers.ListField(required=True)
    customer_receipts = serializers.ListField(required=True)
    customer_receipt_particulars = serializers.ListField(required=True)
    customer_receipt_payments = serializers.ListField(required=True)
    open_air_receipts = serializers.ListField(required=True)
    open_air_receipt_particulars = serializers.ListField(required=True)
    open_air_receipt_payments = serializers.ListField(required=True)
    market_returns = serializers.ListField(required=True)
    bbf = serializers.ListField(required=True)
    returns = serializers.ListField(required=True)
    deposits = serializers.ListField(required=True)
    receipt_misc = serializers.ListField(required=True)
    delivery_date = serializers.DateField(required=True)
    aggregation_center_id = serializers.IntegerField(required=True)

    def create(self, validated_data):
        return super(DataSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        return super(DataSerializer, self).update(instance, validated_data)
