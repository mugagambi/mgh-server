from rest_framework import viewsets
from sales import serializers
from sales import models


# Create your views here.
class RegionViewSet(viewsets.ModelViewSet):
    queryset = models.Region.objects.all()
    serializer_class = serializers.RegionSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = models.Customer.objects.all()
    serializer_class = serializers.CustomerSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer


class OrderProductsViewSet(viewsets.ModelViewSet):
    queryset = models.OrderProducts.objects.all()
    serializer_class = serializers.OrderProductsSerializer


class PackageViewSet(viewsets.ModelViewSet):
    queryset = models.Package.objects.all()
    serializer_class = serializers.PackageSerializer


class PackageProductsViewSet(viewsets.ModelViewSet):
    queryset = models.PackageProduct.objects.all()
    serializer_class = serializers.PackageProductSerializer


class CustomerPriceViewSet(viewsets.ModelViewSet):
    queryset = models.CustomerPrice.objects.all()
    serializer_class = serializers.CustomerPriceSerializer


class CustomerDiscountsViewSet(viewsets.ModelViewSet):
    queryset = models.CustomerDiscount.objects.all()
    serializer_class = serializers.CustomerDiscountSerializer


class SalesCrateViewSet(viewsets.ModelViewSet):
    queryset = models.SalesCrate.objects.all()
    serializer_class = serializers.SalesCrateSerializer


class PackageProductCrateViewSet(viewsets.ModelViewSet):
    queryset = models.PackageProductCrate.objects.all()
    serializer_class = serializers.PackageProductCrateSerializer


class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = models.Receipt.objects.all()
    serializer_class = serializers.ReceiptSerializer


class ReceiptParticularsViewSet(viewsets.ModelViewSet):
    queryset = models.ReceiptParticular.objects.all()
    serializer_class = serializers.ReceiptParticularSerializer


class ReceiptPaymentViewSet(viewsets.ModelViewSet):
    queryset = models.ReceiptPayment.objects.all()
    serializer_class = serializers.ReceiptPaymentSerializer


class CashReceiptViewSet(viewsets.ModelViewSet):
    queryset = models.CashReceipt.objects.all()
    serializer_class = serializers.CashReceiptSerializer


class CashReceiptParticularViewSet(viewsets.ModelViewSet):
    queryset = models.CashReceiptParticular.objects.all()
    serializer_class = serializers.CashReceiptParticularSerializer


class CashReceiptPaymentViewSet(viewsets.ModelViewSet):
    queryset = models.CashReceiptPayment.objects.all()
    serializer_class = serializers.CashReceiptPaymentSerializer


class CreditSettlementViewSet(viewsets.ModelViewSet):
    queryset = models.CreditSettlement.objects.all()
    serializer_class = serializers.CreditSettlementSerializer


class OverPayOrUnderPayViewSet(viewsets.ModelViewSet):
    queryset = models.OverPayOrUnderPay.objects.all()
    serializer_class = serializers.OverPayOrUnderPaySerializer
