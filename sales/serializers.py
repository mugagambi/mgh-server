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
        fields = ('number', 'shop_name', 'nick_name', 'location', 'phone_number', 'email',
                  'region', 'created_at', 'updated_at', 'added_by')


class OrderSerializer(serializers.ModelSerializer):
    received_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.Order
        fields = ('number', 'customer', 'received_by', 'date_delivery', 'created_at', 'updated_at')


class OrderProductsSerializer(serializers.ModelSerializer):
    distributing_qty = serializers.DecimalField(decimal_places=2, max_digits=7, default=0, read_only=True)

    class Meta:
        model = models.OrderProduct
        fields = ('number', 'order', 'product', 'qty', 'price', 'discount', 'distributing_qty')
        read_only_fields = ('price', 'discount')


class PackageSerializer(serializers.ModelSerializer):
    packaged_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.Package
        fields = ('number', 'order', 'packaged_by', 'created_at', 'updated_at')


class PackageProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PackageProduct
        fields = ('number', 'package', 'product', 'order_product', 'qty_weigh', 'crate_weight')
        read_only_fields = ('product',)


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
        fields = ('agent', 'crate', 'date_issued', 'date_returned', 'held_by')

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
        fields = ('number', 'customer', 'date', 'served_by')


class ReceiptParticularSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReceiptParticular
        fields = ('qty', 'product', 'price', 'discount', 'receipt', 'total', 'type')
        read_only_fields = ('total',)


class ReceiptPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReceiptPayment
        fields = ('receipt', 'amount', 'type', 'check_number', 'transaction_id', 'mobile_number', 'date_to_pay',
                  'transfer_code', 'created_at', 'updated_at')


class CashReceiptSerializer(serializers.ModelSerializer):
    served_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.CashReceipt
        fields = ('number', 'date', 'served_by')


class CashReceiptParticularSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CashReceiptParticular
        fields = ('qty', 'product', 'price', 'cash_receipt')


class CashReceiptPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CashReceiptPayment
        fields = (
            'cash_receipt', 'amount', 'type', 'check_number', 'transaction_id', 'mobile_number',
            'transfer_code', 'created_at', 'updated_at')


class CreditSettlementSerializer(serializers.ModelSerializer):
    recorded_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.CreditSettlement
        fields = (
            'number', 'customer', 'type', 'amount', 'check_number', 'transaction_id', 'mobile_number', 'transfer_code',
            'date', 'recorded_by', 'updated_at')


class BBFSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BBF
        fields = ('receipt', 'amount', 'customer')


class ReturnsOrRejectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Return
        fields = ('number'
                  , 'product', 'qty', 'customer', 'description', 'date', 'price', 'reason', 'approved', 'replaced')


class CustomerAccountBalance(serializers.ModelSerializer):
    class Meta:
        model = models.CustomerAccountBalance
        fields = ('customer', 'amount', 'last_modified')


class OrderlessPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderlessPackage
        fields = ('number', 'product', 'qty', 'date')


class MarketReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MarketReturn
        fields = ('number', 'product', 'qty', 'date', 'type')


class CustomerDepositSerializer(serializers.ModelSerializer):
    received_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = models.CustomerDeposit
        fields = (
            'number', 'customer', 'amount', 'date', 'via', 'phone_number', 'transaction_id', 'cheque_number',
            'received_by')


class ReceiptMiscSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReceiptMisc
        fields = ('balance', 'receipt')


class TotalDiscountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomerTotalDiscount
        fields = ('pk', 'customer', 'discount', 'created_at', 'updated_at')
