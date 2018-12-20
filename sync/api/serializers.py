from rest_framework import serializers

from sales.models import Customer, Order, OrderProduct


class CustomerSerializer(serializers.ModelSerializer):
    added_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Customer
        fields = ('number', 'email', 'shop_name', 'nick_name', 'location', 'phone_number',
                  'added_by', 'region')

    def create(self, validated_data):
        return super(CustomerSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        return super(CustomerSerializer, self).update(instance, validated_data)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ('number', 'product', 'order', 'qty', 'price', 'discount')

    def create(self, validated_data):
        return super(OrderItemSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        return super(OrderItemSerializer, self).update(instance, validated_data)


class OrderSerializer(serializers.ModelSerializer):
    received_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    items = OrderItemSerializer(many=True, required=True)

    class Meta:
        model = Order
        fields = ('customer', 'number', 'received_by', 'items')

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
