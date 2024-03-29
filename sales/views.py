import django_filters.rest_framework
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from rest_framework import filters
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from core.models import AggregationCenter, Product
from sales import models
from sales import serializers


# Create your views here.
def receipt(request, pk):
    receipt_item = models.Receipt.objects.get(pk=pk)
    return render(request, 'sales/receipt.html', {'receipt': receipt_item})


class RegionViewSet(viewsets.ModelViewSet):
    queryset = models.Region.objects.all()
    serializer_class = serializers.RegionSerializer


class CustomerFilterSet(django_filters.rest_framework.FilterSet):
    created_between = django_filters.DateTimeFromToRangeFilter(name='created_at',
                                                               label='Created (Between)')

    class Meta:
        model = models.Customer
        fields = ('added_by', 'region', 'number', 'created_at', 'created_between')


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = models.Customer.objects.all()
    serializer_class = serializers.CustomerSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = CustomerFilterSet
    ordering_fields = ('created_at', 'updated_at')

    def perform_create(self, serializer):
        customer = serializer.save()
        products = Product.objects.all()
        customer_prices = [models.CustomerPrice(product=product, price=product.common_price, customer=customer) for
                           product in products]
        models.CustomerPrice.objects.bulk_create(customer_prices)


class OrderFilterSet(django_filters.rest_framework.FilterSet):
    created_between = django_filters.DateTimeFromToRangeFilter(name='created_at',
                                                               label='Created (Between)')
    delivered_between = django_filters.DateFromToRangeFilter(name='created_at',
                                                             label='delivery (Between)')

    class Meta:
        model = models.Order
        fields = ('customer', 'received_by', 'date_delivery', 'created_at', 'created_between',
                  'delivered_between', 'number')


class OrderViewSet(viewsets.ModelViewSet):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = OrderFilterSet
    ordering_fields = ('created_at', 'updated_at', 'date_delivery')


class OrderProductsViewSet(viewsets.ModelViewSet):
    queryset = models.OrderProduct.objects.all()
    serializer_class = serializers.OrderProductsSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('order', 'product', 'order__date_delivery')
    ordering_fields = ('qty',)

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        order = serializer.validated_data['order']
        serializer.validated_data.pop('distributing_qty')
        price = models.CustomerPrice.objects.get(product=product, customer=order.customer)
        try:
            discount = models.CustomerDiscount.objects.get(product=product, customer=order.customer)
        except models.CustomerDiscount.DoesNotExist:
            discount = None
        return serializer.save(price=price, discount=discount)


class PackageFilterSet(django_filters.rest_framework.FilterSet):
    created_between = django_filters.DateTimeFromToRangeFilter(name='created_at',
                                                               label='Created (Between)')

    class Meta:
        model = models.Package
        fields = ('order', 'number', 'packaged_by', 'created_at', 'created_between', 'order__date_delivery')


class PackageViewSet(viewsets.ModelViewSet):
    queryset = models.Package.objects.all()
    serializer_class = serializers.PackageSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = PackageFilterSet
    ordering_fields = ('created_at', 'updated_at')

    def get_serializer(self, *args, **kwargs):
        """ if an array is passed, set serializer to many """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super(PackageViewSet, self).get_serializer(*args, **kwargs)


class PackageProductsViewSet(viewsets.ModelViewSet):
    queryset = models.PackageProduct.objects.all()
    serializer_class = serializers.PackageProductSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('package', 'order_product', 'package__order__date_delivery')
    ordering_fields = ('qty_order', 'qty_weigh', 'crate_weight')

    def get_serializer(self, *args, **kwargs):
        """ if an array is passed, set serializer to many """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super(PackageProductsViewSet, self).get_serializer(*args, **kwargs)


class CustomerPriceViewSet(viewsets.ModelViewSet):
    queryset = models.CustomerPrice.objects.all()
    serializer_class = serializers.CustomerPriceSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('customer', 'product', 'created_at')
    ordering_fields = ('created_at', 'price', 'updated_at')


class CustomerDiscountsViewSet(viewsets.ModelViewSet):
    queryset = models.CustomerDiscount.objects.all()
    serializer_class = serializers.CustomerDiscountSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('customer', 'product', 'created_at')
    ordering_fields = ('created_at', 'discount', 'updated_at')


class SalesCrateFilter(django_filters.rest_framework.FilterSet):
    date_issued_between = django_filters.DateFromToRangeFilter(name='date_issued',
                                                               label='Date Issued(Between)')
    date_returned_between = django_filters.DateFromToRangeFilter(name='date_returned',
                                                                 label='Date Returned (Between)')

    class Meta:
        model = models.SalesCrate
        fields = ('agent', 'date_issued', 'date_returned', 'held_by', 'date_issued_between',
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
        fields = ('customer', 'number', 'date', 'served_by', 'date_between')


class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = models.Receipt.objects.all()
    serializer_class = serializers.ReceiptSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = ReceiptFilterSet
    ordering_fields = ('date',)

    def get_serializer(self, *args, **kwargs):
        """ if an array is passed, set serializer to many """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super(ReceiptViewSet, self).get_serializer(*args, **kwargs)


class ReceiptParticularsViewSet(viewsets.ModelViewSet):
    queryset = models.ReceiptParticular.objects.all()
    serializer_class = serializers.ReceiptParticularSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('product', 'receipt')
    ordering_fields = ('qty', 'price', 'discount')

    def get_serializer(self, *args, **kwargs):
        """ if an array is passed, set serializer to many """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super(ReceiptParticularsViewSet, self).get_serializer(*args, **kwargs)


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

    def get_serializer(self, *args, **kwargs):
        """ if an array is passed, set serializer to many """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super(ReceiptPaymentViewSet, self).get_serializer(*args, **kwargs)


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

    def get_serializer(self, *args, **kwargs):
        """ if an array is passed, set serializer to many """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super(CashReceiptViewSet, self).get_serializer(*args, **kwargs)


class CashReceiptParticularViewSet(viewsets.ModelViewSet):
    queryset = models.CashReceiptParticular.objects.all()
    serializer_class = serializers.CashReceiptParticularSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('product', 'cash_receipt', 'cash_receipt__date')
    ordering_fields = ('qty', 'price')

    def get_serializer(self, *args, **kwargs):
        """ if an array is passed, set serializer to many """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super(CashReceiptParticularViewSet, self).get_serializer(*args, **kwargs)


class CashReceiptPaymentsFilterSet(django_filters.rest_framework.FilterSet):
    created_at_between = django_filters.DateFromToRangeFilter(name='created_at',
                                                              label='Created at (Between)')

    class Meta:
        model = models.CashReceiptPayment
        fields = ('cash_receipt', 'type', 'created_at', 'created_at_between')


class CashReceiptPaymentViewSet(viewsets.ModelViewSet):
    queryset = models.CashReceiptPayment.objects.all()
    serializer_class = serializers.CashReceiptPaymentSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = CashReceiptPaymentsFilterSet
    ordering_fields = ('created_at', 'amount')

    def get_serializer(self, *args, **kwargs):
        """ if an array is passed, set serializer to many """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super(CashReceiptPaymentViewSet, self).get_serializer(*args, **kwargs)


class CreditSettlementViewSet(viewsets.ModelViewSet):
    queryset = models.CreditSettlement.objects.all()
    serializer_class = serializers.CreditSettlementSerializer
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('date', 'amount')


class BBFView(CreateAPIView):
    queryset = models.BBF.objects.all()
    serializer_class = serializers.BBFSerializer

    def perform_create(self, serializer):
        bbf = serializer.save()
        account, created = models.BbfBalance.objects.get_or_create(customer=bbf.customer)
        account.balance = account.balance + bbf.amount
        account.save()


class ReturnsRejectsFilterSet(django_filters.rest_framework.FilterSet):
    date_between = django_filters.DateTimeFromToRangeFilter(name='date',
                                                            label='Date (Between)')

    class Meta:
        model = models.Return
        fields = ('product', 'customer', 'date', 'date_between')


class ReturnsRejectsViewSet(viewsets.ModelViewSet):
    queryset = models.Return.objects.all()
    serializer_class = serializers.ReturnsOrRejectsSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_class = ReturnsRejectsFilterSet
    ordering_fields = ('date', 'qty')

    def perform_create(self, serializer):
        returns = serializer.save()
        if returns.approved:
            returns.approved_by = self.request.user
            returns.save()


@api_view(['GET'])
def distributed_order_product(request, date, center):
    """Distributed """
    center = get_object_or_404(AggregationCenter, pk=center)
    order_distribution_center_products = models.OrderDistributionPoint.objects.filter(center=center,
                                                                                      order_product__order__date_delivery=date)
    order_products = []
    for product in order_distribution_center_products:
        product.order_product.distributing_qty = product.qty
        order_products.append(product.order_product)
    serializer = serializers.OrderProductsSerializer(order_products, many=True)
    return Response(serializer.data)


class CustomerAccountBalanceViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.CustomerAccountBalance.objects.all()
    serializer_class = serializers.CustomerAccountBalance


class OrderlessPackage(viewsets.ModelViewSet):
    queryset = models.OrderlessPackage.objects.all()
    serializer_class = serializers.OrderlessPackageSerializer


class MarketReturnView(viewsets.ModelViewSet):
    queryset = models.MarketReturn.objects.all()
    serializer_class = serializers.MarketReturnSerializer


class CustomerDepositViewSet(viewsets.ModelViewSet):
    queryset = models.CustomerDeposit.objects.all()
    serializer_class = serializers.CustomerDepositSerializer


class ReceiptMiscViewSet(viewsets.ModelViewSet):
    queryset = models.ReceiptMisc.objects.all()
    serializer_class = serializers.ReceiptMiscSerializer


class TotalDiscountViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.CustomerTotalDiscount.objects.all()
    serializer_class = serializers.TotalDiscountsSerializer
