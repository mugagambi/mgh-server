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
