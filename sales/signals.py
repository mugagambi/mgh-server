import datetime
from decimal import Decimal

from django.core.mail import send_mail
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template import loader

from admins.models import Admin
from core.models import Product, AggregationCenterProduct, AggregationCenter
from sales.models import OrderProduct, OrderDistributionPoint, CustomerAccount, CustomerAccountBalance, \
    ReceiptParticular, BBF, Return, ReceiptPayment, CustomerDeposit, Order
from system_settings.models import Settings
from utils import main_generate_unique_id
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
            if AggregationCenterProduct.objects.filter(date=datetime.datetime.today(),
                                                       product=instance.product,
                                                       aggregation_center=center).exists():
                center_product = AggregationCenterProduct.objects.filter(date=datetime.datetime.today(),
                                                                         product=instance.product,
                                                                         aggregation_center=center).first()
                if int(center_product.remaining) > 1:
                    center_product.remaining = center_product.remaining - instance.qty
                    OrderDistributionPoint.objects.create(order_product=instance,
                                                          qty=instance.qty,
                                                          center=center)
                    center_product.save()
                    break
                else:
                    continue
            else:
                continue
        if not OrderDistributionPoint.objects.filter(order_product=instance).exists():
            main_center = Settings.objects.all().first().main_distribution
            OrderDistributionPoint.objects.create(order_product=instance,
                                                  qty=instance.qty,
                                                  center=main_center)

    elif not created:
        current_distribution = OrderDistributionPoint.objects.filter(order_product=instance).aggregate(total=Sum('qty'))
        to_distribute = instance.qty - current_distribution['total']
        for center in centers:
            if AggregationCenterProduct.objects.filter(date=datetime.datetime.today(),
                                                       product=instance.product,
                                                       aggregation_center=center).exists():
                center_product = AggregationCenterProduct.objects.filter(date=datetime.datetime.today(),
                                                                         product=instance.product,
                                                                         aggregation_center=center).first()
                if center_product.remaining > 0.0:
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
                else:
                    try:
                        distribution = OrderDistributionPoint.objects.get(order_product=instance, center=center)
                        final_qty = distribution.qty + to_distribute
                        distribution.qty = final_qty
                        distribution.save()
                    except OrderDistributionPoint.DoesNotExist:
                        pass
                    break
            else:
                continue


@receiver(post_save, sender=CustomerAccount)
def update_customer_balance(sender, instance, created, **kwargs):
    if created:
        balance, created = CustomerAccountBalance.objects.get_or_create(customer=instance.customer)
        balance.amount = balance.amount + instance.amount
        balance.save()


@receiver(post_save, sender=ReceiptParticular)
def particular_account(sender, instance, created, **kwargs):
    if created:
        CustomerAccount.objects.create(number=main_generate_unique_id(),
                                       customer=instance.receipt.customer,
                                       amount=-instance.total,
                                       date=instance.receipt.date,
                                       type='P',
                                       receipt=instance.receipt)


@receiver(post_save, sender=BBF)
def bbf_account(sender, instance, created, **kwargs):
    if created:
        CustomerAccount.objects.create(number=main_generate_unique_id(),
                                       customer=instance.customer,
                                       amount=instance.amount,
                                       date=instance.date,
                                       type='B')


@receiver(post_save, sender=Return)
def return_account(sender, instance, created, **kwargs):
    if created:
        if not instance.replaced:
            CustomerAccount.objects.create(number=main_generate_unique_id(),
                                           customer=instance.customer,
                                           amount=Decimal(instance.qty) * Decimal(instance.price),
                                           date=instance.date,
                                           type='R',
                                           returns=instance)
    else:
        if not instance.replaced and not CustomerAccount.objects.filter(returns=instance).exists():
            CustomerAccount.objects.create(number=main_generate_unique_id(),
                                           customer=instance.customer,
                                           amount=Decimal(instance.qty) * Decimal(instance.price),
                                           date=instance.date,
                                           type='R',
                                           returns=instance)


@receiver(post_save, sender=ReceiptPayment)
def receipt_payment_account(sender, instance, created, **kwargs):
    if created:
        if instance.type == 1:
            type = 'Q'
            cheque_number = instance.check_number
            transaction_id = ''
            phone_number = ''
        elif instance.type == 2:
            type = 'M'
            cheque_number = ''
            transaction_id = instance.transaction_id
            phone_number = instance.mobile_number
        elif instance.type == 3:
            type = 'C'
            cheque_number = ''
            transaction_id = ''
            phone_number = ''
        elif instance.type == 5:
            type = 'B'
            cheque_number = ''
            transaction_id = ''
            phone_number = ''
        else:
            type = ''
            cheque_number = ''
            transaction_id = ''
            phone_number = ''
        if instance.type != 4:
            CustomerAccount.objects.create(number=main_generate_unique_id(),
                                           customer=instance.receipt.customer,
                                           amount=instance.amount,
                                           date=instance.receipt.date,
                                           type='A',
                                           via=type,
                                           receipt=instance.receipt,
                                           cheque_number=cheque_number,
                                           transaction_id=transaction_id,
                                           phone_number=phone_number)


@receiver(post_save, sender=CustomerDeposit)
def deposit_account(sender, instance, created, **kwargs):
    if created:
        instance.remaining_amount = instance.amount
        instance.save()
        CustomerAccount.objects.create(number=main_generate_unique_id(),
                                       customer=instance.customer,
                                       amount=instance.amount,
                                       date=instance.date,
                                       type='D',
                                       via=instance.via,
                                       cheque_number=instance.cheque_number,
                                       transaction_id=instance.transaction_id,
                                       phone_number=instance.phone_number)


# @receiver(post_save, sender=Order)
# def check_order_duplicates(sender, instance, created, **kwargs):
#     """Send an email to admins when an order duplicate is detected."""
#     orders = Order.objects.filter(customer=instance.customer, date_delivery=instance.date_delivery)
#     if orders.exists():
#         """send an alert email to admins"""
#         subject = f'Order duplication for {instance.customer.shop_name}'
#         message = 'You need an email client with html capabilities to read this email'
#         admins = Admin.objects.all()
#         recepients = admins.values_list('email', flat=True)
#         html_message = loader.render_to_string(
#             'sales/orders/order_duplication_alert_email.html',
#             {
#                 'orders': orders
#             }
#         )
#         if admins.exists():
#             send_mail(
#                 subject=subject,
#                 message=message,
#                 from_email='mghbot@gmail.com',
#                 recipient_list=recepients,
#                 html_message=html_message
#             )
