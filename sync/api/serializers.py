from rest_framework import serializers


class CustomerSerializer(serializers.Serializer):
    number = serializers.CharField(max_length=10, required=True)
    shop_name = serializers.CharField(max_length=100, required=True)
    nick_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    location = serializers.CharField(max_length=100, required=True)
    phone_number = serializers.CharField(max_length=100, required=False, allow_blank=True)
    region = serializers.IntegerField(required=True)

    def create(self, validated_data):
        return super(CustomerSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        return super(CustomerSerializer, self).update(instance, validated_data)


class OrderSerializer(serializers.Serializer):
    number = serializers.CharField(max_length=10, required=True)
    customer = serializers.CharField(max_length=10, required=True)
    date_delivery = serializers.DateField(required=True)

    def create(self, validated_data):
        return super(OrderSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        return super(OrderSerializer, self).update(instance, validated_data)


class DataSerializer(serializers.Serializer):
    customers = CustomerSerializer(many=True, required=True)
    orders = OrderSerializer(many=True, required=True)

    def create(self, validated_data):
        return super(DataSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        return super(DataSerializer, self).update(instance, validated_data)
