from django.contrib import admin
from sales import models


class RegionAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name',)


class CustomerPriceInline(admin.TabularInline):
    model = models.CustomerPrice
    can_delete = True
    autocomplete_fields = ('product',)
    extra = 1
    verbose_name = 'Price'
    verbose_name_plural = 'Prices'


class CustomerDiscountInline(admin.TabularInline):
    model = models.CustomerDiscount
    can_delete = True
    autocomplete_fields = ('product',)
    extra = 1
    verbose_name = 'Discount'
    verbose_name_plural = 'Discounts'


class CustomerAdmin(admin.ModelAdmin):
    inlines = [CustomerPriceInline, CustomerDiscountInline]
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
    verbose_name = 'Item'
    verbose_name_plural = 'Items'


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


class SalesCrateAdmin(admin.ModelAdmin):
    list_display = ('agent', 'crate', 'date_issued', 'date_returned', 'held_by')
    list_filter = ('agent', 'crate', 'date_issued', 'date_returned', 'held_by')
    list_per_page = 20


class SalesAdmin(admin.ModelAdmin):
    list_per_page = 50
    list_filter = ('customer', 'served_by', 'date')
    date_hierarchy = 'date'
    list_display = ('customer', 'served_by', 'date')
    exclude = ('customer', 'served_by', 'date')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Register your models here.
admin.site.register(models.Region, RegionAdmin)
admin.site.register(models.Customer, CustomerAdmin)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.SalesCrate)
admin.site.register(models.CreditSettlement)
admin.site.register(models.OverPayOrUnderPay)
admin.site.register(models.ReturnsOrRejects)
admin.site.register(models.Receipt, SalesAdmin)
