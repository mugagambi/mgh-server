from django.contrib import admin
from sales import models

# Register your models here.
admin.site.register(models.Region)
admin.site.register(models.Customer)
admin.site.register(models.Order)
admin.site.register(models.OrderProducts)
admin.site.register(models.Package)
admin.site.register(models.PackageProduct)
admin.site.register(models.CustomerPrice)
admin.site.register(models.CustomerDiscount)
admin.site.register(models.SalesCrate)
admin.site.register(models.PackageProductCrate)
admin.site.register(models.Receipt)
admin.site.register(models.ReceiptParticular)
admin.site.register(models.ReceiptPayment)
admin.site.register(models.CashReceipt)
admin.site.register(models.CashReceiptParticular)
admin.site.register(models.CashReceiptPayment)
admin.site.register(models.CreditSettlement)
admin.site.register(models.OverPayOrUnderPay)
admin.site.register(models.ReturnsOrRejects)







