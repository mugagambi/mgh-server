from rest_framework import serializers
from sales import models


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Region
        fields = ('id', 'name',)


class CustomerSerializer(serializers.ModelSerializer):
    added_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.Customer
        fields = ('id', 'shop_name', 'nick_name', 'location', 'country_code', 'phone_number',
                  'region', 'created_at', 'updated_at', 'added_by')


class OrderSerializer(serializers.ModelSerializer):
    received_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.Order
        fields = ('id', 'customer', 'received_by', 'date_delivery', 'created_at', 'updated_at')


class OrderProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderProducts
        fields = ('id', 'order', 'product', 'qty', 'price')


class PackageSerializer(serializers.ModelSerializer):
    packaged_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.Package
        fields = ('id', 'order', 'packaged_by', 'created_at', 'updated_at')


class PackageProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PackageProduct
        fields = ('id', 'package', 'product', 'qty_order', 'qty_weigh', 'crate_weight')


class CustomerPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomerPrice
        fields = ('id', 'customer', 'price', 'product', 'created_at', 'updated_at')


class CustomerDiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomerDiscount
        fields = ('id', 'customer', 'discount', 'product', 'created_at', 'updated_at')


class SalesCrateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SalesCrate
        fields = ('id', 'agent', 'crate', 'date_issued', 'date_returned', 'held_by')

    def validate_agent(self, value):
        if not value.is_sales_agent:
            raise serializers.ValidationError('agent must be a sales agent')
        return value


class PackageProductCrateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PackageProductCrate
        fields = ('id', 'crate', 'package_product')


class ReceiptSerializer(serializers.ModelSerializer):
    served_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.Receipt
        fields = ('id', 'customer', 'date', 'served_by')


class ReceiptParticularSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReceiptParticular
        fields = ('id', 'qty', 'product', 'price', 'discount', 'receipt')


class ReceiptPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReceiptPayment
        fields = ('id', 'receipt', 'amount', 'type', 'check_number', 'transaction_id', 'mobile_number', 'date_to_pay',
                  'transfer_code', 'created_at', 'updated_at')


class CashReceiptSerializer(serializers.ModelSerializer):
    served_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.CashReceipt
        fields = ('id', 'date', 'served_by')


class CashReceiptParticularSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CashReceiptParticular
        fields = ('id', 'qty', 'product', 'price', 'discount', 'cash_receipt')


class CashReceiptPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CashReceiptPayment
        fields = (
            'id', 'cash_receipt', 'amount', 'type', 'check_number', 'transaction_id', 'mobile_number', 'date_to_pay',
            'transfer_code', 'created_at', 'updated_at')


class CreditSettlementSerializer(serializers.ModelSerializer):
    served_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.CreditSettlement
        fields = ('id', 'receipt', 'amount', 'date', 'served_by')


class OverPayOrUnderPaySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OverPayOrUnderPay
        fields = ('id', 'type', 'customer', 'receipt', 'amount', 'date')


class ReturnsOrRejectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReturnsOrRejects
        fields = (
            'id', 'type', 'product', 'qty', 'receipt', 'customer', 'description', 'date', 'date_of_resuplly')
