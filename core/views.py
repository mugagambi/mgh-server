import django_filters.rest_framework
from rest_framework import viewsets
from core import models
from core import serializers
from rest_framework import filters

from core.serializers import UserSerializer


# TODO send permissions short codes with the token payload
def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data
    }


# Create your views here.
class AggregationCenterViewSet(viewsets.ModelViewSet):
    """
       retrieve:
       Return the given aggregation center.
       list:
       Return a list of all the existing aggregation centers.
       create:
       Create a new aggregation center instance.
       update:
       Update the given aggregation center
       """
    queryset = models.AggregationCenter.objects.all()
    serializer_class = serializers.AggregationCenterSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
           retrieve:
           Return the given product.
           list:
           Return a list of all the existing product.
           create:
           Create a new product instance.
           update:
           Update the given product
           """
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer


class AggregationCenterProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
               retrieve:
               Return the given aggregation center product.
               list:
               Return a list of all the existing aggregation centers products.
               create:
               Create a new aggregation center product instance.
               update:
               Update the given aggregation center product
               """
    queryset = models.AggregationCenterProduct.objects.all()
    serializer_class = serializers.AggregationCenterProductSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter)
    filter_fields = ('aggregation_center', 'product',)
    ordering_fields = ('id',)


class CrateTypeViewSet(viewsets.ModelViewSet):
    queryset = models.CrateType.objects.all()
    serializer_class = serializers.CrateTypeSerializer
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('weight',)


class CrateViewSet(viewsets.ModelViewSet):
    queryset = models.Crate.objects.all()
    serializer_class = serializers.CrateSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('type',)
