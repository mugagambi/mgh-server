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


class PackageSerializer(serializers.ModelSerializer):
    packaged_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.Package
        fields = ('order', 'packaged_by', 'created_at', 'updated_at')


class PackageProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PackageProduct
        fields = ('package', 'product', 'qty_order', 'qty_weigh', 'crate_weight', 'grade')


class CustomerPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomerPrice
        fields = ('customer', 'price', 'product', 'grade', 'grade', 'created_at', 'updated_at')


class CustomerDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomerDiscount
        fields = ('customer', 'discount', 'product', 'grade', 'created_at', 'updated_at')


class SalesCrateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SalesCrate
        fields = ('agent', 'crate', 'date_issued', 'date_returned', 'held_by')

    def validate_agent(self, value):
        if not value.is_sales_agent:
            raise serializers.ValidationError('agent must be a sales agent')
        return value


class PackageProductCrateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PackageProductCrate
        fields = ('crate', 'package_product')


class ReceiptSerializer(serializers.ModelSerializer):
    served_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.Receipt
        fields = ('customer', 'date', 'served_by')


class ReceiptParticularSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReceiptParticular
        fields = ('qty', 'product', 'price', 'grade', 'discount', 'receipt')
