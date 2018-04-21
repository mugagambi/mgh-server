from django.dispatch import receiver
from django.db.models.signals import post_save
from core.models import AggregationCenterProduct


@receiver(post_save, sender=AggregationCenterProduct)
def update_remaining_units(sender, instance, created, **kwargs):
    if created:
        instance.remaining = instance.qty
        instance.save()
