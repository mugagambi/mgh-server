from django.contrib import admin
from sales import models


class RegionAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name',)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'country_code', 'phone_number',
                    'added_by', 'region', 'created_at', 'updated_at')
    fields = ('name', 'location', ('country_code', 'phone_number'), 'region')
    list_filter = ('country_code', 'region', 'added_by', 'created_at')
    autocomplete_fields = ('region',)
    search_fields = ('name',)
    date_hierarchy = 'created_at'
    list_select_related = True

    def save_model(self, request, obj, form, change):
        obj.added_by = request.user
        super(CustomerAdmin, self).save_model(request, obj, form, change)


class OrderProductsInline(admin.TabularInline):
    model = models.OrderProducts
    can_delete = True
    autocomplete_fields = ('product',)
    extra = 1
    verbose_name = 'Order Product'
    verbose_name_plural = 'Order Products'


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderProductsInline]
    list_display = ('customer', 'received_by', 'date_delivery', 'created_at', 'updated_at')
    fields = ('customer', 'date_delivery')
    autocomplete_fields = ('customer',)
    list_filter = ('customer', 'received_by', 'date_delivery', 'created_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 20

    def save_model(self, request, obj, form, change):
        obj.received_by = request.user
        super(OrderAdmin, self).save_model(request, obj, form, change)


class CustomerPriceAdmin(admin.ModelAdmin):
    list_display = ('customer', 'price', 'product', 'created_at', 'updated_at')
    fields = ('customer', 'price', 'product')
    list_filter = ('customer', 'product', 'created_at', 'updated_at')
    autocomplete_fields = ('customer', 'product')
    date_hierarchy = 'created_at'
    list_per_page = 20
    list_select_related = True


class SalesCrateAdmin(admin.ModelAdmin):
    list_display = ('agent', 'crate', 'date_issued', 'date_returned', 'held_by')
    list_filter = ('agent', 'crate', 'date_issued', 'date_returned', 'held_by')
    list_per_page = 20


class CustomerDiscountAdmin(admin.ModelAdmin):
    list_display = ('customer', 'discount', 'product', 'created_at', 'updated_at')
    fields = ('customer', 'discount', 'product')
    list_filter = ('customer', 'product', 'created_at', 'updated_at')
    autocomplete_fields = ('customer', 'product')
    date_hierarchy = 'created_at'
    list_per_page = 20
    list_select_related = True


# Register your models here.
admin.site.register(models.Region, RegionAdmin)
admin.site.register(models.Customer, CustomerAdmin)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.CustomerPrice, CustomerPriceAdmin)
admin.site.register(models.CustomerDiscount, CustomerDiscountAdmin)
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
