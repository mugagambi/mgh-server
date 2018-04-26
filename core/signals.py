from django.dispatch import receiver
from django.db.models.signals import post_save
from core.models import AggregationCenterProduct, Product
from sales.models import Customer, CustomerPrice


@receiver(post_save, sender=AggregationCenterProduct)
def update_remaining_units(sender, instance, created, **kwargs):
    if created:
        instance.remaining = instance.qty
        instance.save()


@receiver(post_save, sender=Product)
def add_prices_to_customers(sender, instance, created, **kwargs):
    if created:
        customers = Customer.objects.all()
        for customer in customers:
            CustomerPrice.objects.create(customer=customer, product=instance,
                                         price=instance.common_price)
