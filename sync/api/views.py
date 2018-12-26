from django.db import transaction
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from core import models
from core import serializers as core_serializers
from sales import serializers
from sales.models import Customer, Order, OrderProduct, Package, PackageProduct, Receipt, ReceiptParticular, \
    ReceiptPayment, CashReceipt, CashReceiptParticular, CashReceiptPayment, MarketReturn, BBF, Return, CustomerDeposit, \
    ReceiptMisc, Region, CustomerPrice, OrderDistributionPoint, CustomerAccountBalance
from sync.tasks import backup
from .serializers import DataSerializer


def save_objects(serializer, model):
    """
    Given a serializer and a model class, bulk create the validated items on the serializer
    :param serializer:
    :param model:
    :return:
    """
    objects_list = serializer.validated_data
    objects = []
    for item in objects_list:
        if 'distributing_qty' in item:
            item.pop('distributing_qty')
        objects.append(model(**item))
    model.objects.bulk_create(objects)


def entity_objects():
    """
    Return a list of entity objects
    :return: List
    """
    return [
        {
            "entity": 'customers',
            'serializer_class': serializers.CustomerSerializer,
            'model_class': Customer
        },
        {
            "entity": 'orders',
            'serializer_class': serializers.OrderSerializer,
            'model_class': Order
        },
        {
            "entity": 'order_products',
            'serializer_class': serializers.OrderProductsSerializer,
            'model_class': OrderProduct
        },
        {
            "entity": 'packages',
            'serializer_class': serializers.PackageSerializer,
            'model_class': Package
        },
        {
            "entity": 'package_products',
            'serializer_class': serializers.PackageProductSerializer,
            'model_class': PackageProduct
        },
        {
            "entity": 'package_products',
            'serializer_class': serializers.PackageProductSerializer,
            'model_class': PackageProduct
        },
        {
            "entity": 'customer_receipts',
            'serializer_class': serializers.ReceiptSerializer,
            'model_class': Receipt
        },
        {
            "entity": 'customer_receipt_particulars',
            'serializer_class': serializers.ReceiptParticularSerializer,
            'model_class': ReceiptParticular
        },
        {
            "entity": 'customer_receipt_payments',
            'serializer_class': serializers.ReceiptPaymentSerializer,
            'model_class': ReceiptPayment
        },
        {
            "entity": 'open_air_receipts',
            'serializer_class': serializers.CashReceiptSerializer,
            'model_class': CashReceipt
        },
        {
            "entity": 'open_air_receipt_particulars',
            'serializer_class': serializers.CashReceiptParticularSerializer,
            'model_class': CashReceiptParticular
        },
        {
            "entity": 'open_air_receipt_payments',
            'serializer_class': serializers.CashReceiptPaymentSerializer,
            'model_class': CashReceiptPayment
        },
        {
            "entity": 'market_returns',
            'serializer_class': serializers.MarketReturnSerializer,
            'model_class': MarketReturn
        },
        {
            "entity": 'bbf',
            'serializer_class': serializers.BBFSerializer,
            'model_class': BBF
        },
        {
            "entity": 'returns',
            'serializer_class': serializers.ReturnsOrRejectsSerializer,
            'model_class': Return
        },
        {
            "entity": 'deposits',
            'serializer_class': serializers.CustomerDepositSerializer,
            'model_class': CustomerDeposit
        },
        {
            "entity": 'receipt_misc',
            'serializer_class': serializers.ReceiptMiscSerializer,
            'model_class': ReceiptMisc
        }
    ]


def generate_entity_response(queryset, serializer_class):
    """
    Given a queryset return a json serialized object
    :param queryset:
    :param serializer_class:
    :return:
    """
    serializer = serializer_class(queryset, many=True)
    return serializer.data


def response_items(delivery_date, aggregation_center_id):
    """
    sync response objects
    :param delivery_date:
    :param aggregation_center_id:
    :return:
    """
    center = get_object_or_404(models.AggregationCenter, pk=aggregation_center_id)
    order_distribution_center_products = OrderDistributionPoint.objects.filter(center=center,
                                                                               order_product__order__date_delivery=delivery_date)
    order_products = []
    for product in order_distribution_center_products:
        product.order_product.distributing_qty = product.qty
        order_products.append(product.order_product)

    return [
        {
            "item": "aggregation_centers",
            "queryset": models.AggregationCenter.objects.all(),
            'serializer_class': core_serializers.AggregationCenterSerializer
        },
        {
            "item": "products",
            "queryset": models.Product.objects.all(),
            'serializer_class': core_serializers.ProductSerializer
        },
        {
            "item": "regions",
            "queryset": Region.objects.all(),
            'serializer_class': serializers.RegionSerializer
        },
        {
            "item": "customers",
            "queryset": Customer.objects.all(),
            'serializer_class': serializers.CustomerSerializer
        },
        {
            "item": "orders",
            "queryset": Order.objects.filter(date_delivery=delivery_date),
            'serializer_class': serializers.OrderSerializer
        },
        {
            "item": "customer_prices",
            "queryset": CustomerPrice.objects.all(),
            'serializer_class': serializers.CustomerSerializer
        },
        {
            "item": "order_products",
            "queryset": order_products,
            'serializer_class': serializers.OrderProductsSerializer
        },
        {
            "item": "packages",
            "queryset": Package.objects.filter(order__date_delivery=delivery_date),
            'serializer_class': serializers.PackageSerializer
        },
        {
            "item": "package_products",
            "queryset": PackageProduct.objects.filter(order__date_delivery=delivery_date),
            'serializer_class': serializers.PackageSerializer
        },
        {
            "item": "customer_balances",
            "queryset": CustomerAccountBalance.objects.all(),
            'serializer_class': serializers.CustomerAccountBalance
        }
    ]


def response(delivery_date, aggregation_center_id):
    """
    Response to return after posting sync data
    :return:
    """
    json_response = {}
    for item in response_items(delivery_date, aggregation_center_id):
        json_response[item['entity']] = generate_entity_response(queryset=item['queryset'],
                                                                 serializer_class=item['serializer_class'])
    return json_response


# todo add orderless when posting sync
@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
@transaction.atomic
def sync_data(request, format=None):
    print(request.data)
    serializer = DataSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        for entity_object in entity_objects():
            entity_serializer = entity_object['serializer_class'](data=request.data[entity_object['entity']], many=True,
                                                                  context={'request': request})
            if entity_serializer.is_valid():
                save_objects(serializer=entity_serializer, model=entity_object['model_class'])
            else:
                return Response(entity_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        backup.delay()
        return Response({'message': 'successfully synchronized',
                         'response': response(delivery_date=serializer.validated_data['delivery_date'],
                                              aggregation_center_id=serializer.validated_data[
                                                  'aggregation_center_id'])}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
