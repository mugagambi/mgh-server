from rest_framework import viewsets
from sales import serializers
from sales import models
import django_filters.rest_framework
from rest_framework import filters


# Create your views here.
class RegionViewSet(viewsets.ModelViewSet):
    queryset = models.Region.objects.all()
    serializer_class = serializers.RegionSerializer


class CustomerFilterSet(django_filters.rest_framework.FilterSet):
    created_between = django_filters.DateTimeFromToRangeFilter(name='created_at',
                                                               label='Created (Between)')

    class Meta:
        model = models.Customer
        fields = ('country_code', 'added_by', 'region', 'created_at', 'created_between')


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = models.Customer.objects.all()
    serializer_class = serializers.CustomerSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = CustomerFilterSet
    ordering_fields = ('created_at', 'updated_at')


class OrderFilterSet(django_filters.rest_framework.FilterSet):
    created_between = django_filters.DateTimeFromToRangeFilter(name='created_at',
                                                               label='Created (Between)')
    delivered_between = django_filters.DateFromToRangeFilter(name='created_at',
                                                             label='delivery (Between)')

    class Meta:
        model = models.Order
        fields = ('customer', 'received_by', 'date_delivery', 'created_at', 'created_between',
                  'delivered_between')


class OrderViewSet(viewsets.ModelViewSet):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = OrderFilterSet
    ordering_fields = ('created_at', 'updated_at', 'date_delivery')


class OrderProductsViewSet(viewsets.ModelViewSet):
    queryset = models.OrderProducts.objects.all()
    serializer_class = serializers.OrderProductsSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('order', 'product', 'grade')
    ordering_fields = ('qty', 'price')


class PackageFilterSet(django_filters.rest_framework.FilterSet):
    created_between = django_filters.DateTimeFromToRangeFilter(name='created_at',
                                                               label='Created (Between)')

    class Meta:
        model = models.Package
        fields = ('order', 'packaged_by', 'created_at', 'created_between')


class PackageViewSet(viewsets.ModelViewSet):
    queryset = models.Package.objects.all()
    serializer_class = serializers.PackageSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = PackageFilterSet
    ordering_fields = ('created_at', 'updated_at')


class PackageProductsViewSet(viewsets.ModelViewSet):
    queryset = models.PackageProduct.objects.all()
    serializer_class = serializers.PackageProductSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('package', 'product', 'grade')
    ordering_fields = ('qty_order', 'qty_weigh', 'crate_weight')


class CustomerPriceViewSet(viewsets.ModelViewSet):
    queryset = models.CustomerPrice.objects.all()
    serializer_class = serializers.CustomerPriceSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('customer', 'product', 'grade', 'created_at')
    ordering_fields = ('created_at', 'price', 'updated_at')


class CustomerDiscountsViewSet(viewsets.ModelViewSet):
    queryset = models.CustomerDiscount.objects.all()
    serializer_class = serializers.CustomerDiscountSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('customer', 'product', 'grade', 'created_at')
    ordering_fields = ('created_at', 'discount', 'updated_at')


class SalesCrateFilter(django_filters.rest_framework.FilterSet):
    date_issued_between = django_filters.DateFromToRangeFilter(name='date_issued',
                                                               label='Date Issued(Between)')
    date_returned_between = django_filters.DateFromToRangeFilter(name='date_returned',
                                                                 label='Date Returned (Between)')

    class Meta:
        model = models.SalesCrate
        fields = ('agent', 'crate', 'date_issued', 'date_returned', 'held_by', 'date_issued_between',
                  'date_returned_between')


class SalesCrateViewSet(viewsets.ModelViewSet):
    queryset = models.SalesCrate.objects.all()
    serializer_class = serializers.SalesCrateSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = SalesCrateFilter
    ordering_fields = ('date_issued', 'date_returned')


class PackageProductCrateViewSet(viewsets.ModelViewSet):
    queryset = models.PackageProductCrate.objects.all()
    serializer_class = serializers.PackageProductCrateSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('crate', 'package_product')


class ReceiptFilterSet(django_filters.rest_framework.FilterSet):
    date_between = django_filters.DateTimeFromToRangeFilter(name='date',
                                                            label='Date (Between)')

    class Meta:
        model = models.Receipt
        fields = ('customer', 'date', 'served_by', 'date_between')


class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = models.Receipt.objects.all()
    serializer_class = serializers.ReceiptSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = ReceiptFilterSet
    ordering_fields = ('date',)


class ReceiptParticularsViewSet(viewsets.ModelViewSet):
    queryset = models.ReceiptParticular.objects.all()
    serializer_class = serializers.ReceiptParticularSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('grade', 'product', 'receipt')
    ordering_fields = ('qty', 'price', 'discount')


class ReceiptPaymentsFilterSet(django_filters.rest_framework.FilterSet):
    date_to_pay_between = django_filters.DateFromToRangeFilter(name='date_to_pay',
                                                               label='Date to pay (Between)')
    created_at_between = django_filters.DateFromToRangeFilter(name='created_at',
                                                              label='Created at (Between)')

    class Meta:
        model = models.ReceiptPayment
        fields = ('receipt', 'date_to_pay', 'type', 'created_at', 'date_to_pay_between', 'created_at_between')


class ReceiptPaymentViewSet(viewsets.ModelViewSet):
    queryset = models.ReceiptPayment.objects.all()
    serializer_class = serializers.ReceiptPaymentSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = ReceiptPaymentsFilterSet
    ordering_fields = ('created_at', 'amount', 'date_to_pay')


class CashReceiptFilterSet(django_filters.rest_framework.FilterSet):
    date_between = django_filters.DateTimeFromToRangeFilter(name='date',
                                                            label='Date (Between)')

    class Meta:
        model = models.CashReceipt
        fields = ('date', 'served_by', 'date_between')


class CashReceiptViewSet(viewsets.ModelViewSet):
    queryset = models.CashReceipt.objects.all()
    serializer_class = serializers.CashReceiptSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = CashReceiptFilterSet
    ordering_fields = ('date',)


class CashReceiptParticularViewSet(viewsets.ModelViewSet):
    queryset = models.CashReceiptParticular.objects.all()
    serializer_class = serializers.CashReceiptParticularSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('grade', 'product', 'cash_receipt')
    ordering_fields = ('qty', 'price', 'discount')


class CashReceiptPaymentsFilterSet(django_filters.rest_framework.FilterSet):
    date_to_pay_between = django_filters.DateFromToRangeFilter(name='date_to_pay',
                                                               label='Date to pay (Between)')
    created_at_between = django_filters.DateFromToRangeFilter(name='created_at',
                                                              label='Created at (Between)')

    class Meta:
        model = models.CashReceiptPayment
        fields = ('cash_receipt', 'date_to_pay', 'type', 'created_at', 'date_to_pay_between', 'created_at_between')


class CashReceiptPaymentViewSet(viewsets.ModelViewSet):
    queryset = models.CashReceiptPayment.objects.all()
    serializer_class = serializers.CashReceiptPaymentSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = CashReceiptPaymentsFilterSet
    ordering_fields = ('created_at', 'amount', 'date_to_pay')


class CreditSettlementFilterSet(django_filters.rest_framework.FilterSet):
    date_between = django_filters.DateTimeFromToRangeFilter(name='date',
                                                            label='Date (Between)')

    class Meta:
        model = models.CreditSettlement
        fields = ('receipt', 'served_by', 'date', 'date_between')


class CreditSettlementViewSet(viewsets.ModelViewSet):
    queryset = models.CreditSettlement.objects.all()
    serializer_class = serializers.CreditSettlementSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = CreditSettlementFilterSet
    ordering_fields = ('date', 'amount')


class OverPayOrUnderPayFilterSet(django_filters.rest_framework.FilterSet):
    date_between = django_filters.DateTimeFromToRangeFilter(name='date',
                                                            label='Date (Between)')

    class Meta:
        model = models.OverPayOrUnderPay
        fields = ('type', 'customer', 'receipt', 'date', 'date_between')


class OverPayOrUnderPayViewSet(viewsets.ModelViewSet):
    queryset = models.OverPayOrUnderPay.objects.all()
    serializer_class = serializers.OverPayOrUnderPaySerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = OverPayOrUnderPayFilterSet
    ordering_fields = ('date', 'amount')


class ReturnsRejectsFilterSet(django_filters.rest_framework.FilterSet):
    date_between = django_filters.DateTimeFromToRangeFilter(name='date',
                                                            label='Date (Between)')
    resupply_between = django_filters.DateFromToRangeFilter(name='date_of_resuplly',
                                                            label='Resupply (Between)')

    class Meta:
        model = models.ReturnsOrRejects
        fields = ('type', 'product', 'receipt', 'customer', 'date', 'grade', 'date_of_resuplly'
                  , 'date_between', 'resupply_between')


class ReturnsRejectsViewSet(viewsets.ModelViewSet):
    queryset = models.ReturnsOrRejects.objects.all()
    serializer_class = serializers.ReturnsOrRejectsSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = ReturnsRejectsFilterSet
    ordering_fields = ('date', 'qty', 'date_of_resuplly')
