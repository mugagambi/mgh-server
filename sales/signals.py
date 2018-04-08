from django.db.models.signals import post_save
from core.models import Product
from django.dispatch import receiver
from .models import CustomerPrice


@receiver(post_save, sender=Product)
def update_common_price(sender, instance, created, **kwargs):
    if not created:
        prices = CustomerPrice.objects.filter(product=instance, negotiated_price=False)
        for price in prices:
            price.price = instance.common_price
            price.save()
