from django.db.models import Sum
from django.db.models.signals import post_save
from core.models import Product, AggregationCenterProduct, AggregationCenter
from sales.models import OrderProduct, OrderDistributionPoint
from system_settings.models import Settings
from django.dispatch import receiver
from .models import CustomerPrice


@receiver(post_save, sender=Product)
def update_common_price(sender, instance, created, **kwargs):
    if not created:
        prices = CustomerPrice.objects.filter(product=instance, negotiated_price=False)
        for price in prices:
            price.price = instance.common_price
            price.save()


@receiver(post_save, sender=OrderProduct)
def distribute_order(sender, instance, created, **kwargs):
    centers = AggregationCenter.objects.all()
    if created:
        for center in centers:
            try:
                center_product = AggregationCenterProduct.objects.get(aggregation_center=center,
                                                                      product=instance.product)
                if center_product.remaining > 0:
                    center_product.remaining = center_product.remaining - instance.qty
                    center_product.save()
                    OrderDistributionPoint.objects.create(order_product=instance,
                                                          qty=instance.qty,
                                                          center=center)
                    break
            except AggregationCenterProduct.DoesNotExist:
                pass
        if not OrderDistributionPoint.objects.filter(order_product=instance).exists():
            main_center = Settings.objects.all().first().main_distribution
            OrderDistributionPoint.objects.create(order_product=instance,
                                                  qty=instance.qty,
                                                  center=main_center)
    elif not created:
        current_distribution = OrderDistributionPoint.objects.filter(order_product=instance).aggregate(total=Sum('qty'))
        to_distribute = instance.qty - current_distribution['total']
        for center in centers:
            try:
                center_product = AggregationCenterProduct.objects.get(aggregation_center=center,
                                                                      product=instance.product)
                if center_product.remaining > 0:
                    center_product.remaining = center_product.remaining - to_distribute
                    center_product.save()
                    try:
                        distribution = OrderDistributionPoint.objects.get(order_product=instance, center=center)
                        final_qty = distribution.qty + to_distribute
                        distribution.qty = final_qty
                        distribution.save()
                    except OrderDistributionPoint.DoesNotExist:
                        pass
                    break
            except AggregationCenterProduct.DoesNotExist:
                pass
