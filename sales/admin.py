from django.contrib import admin
from sales import models
from utils import InputFilter
from django.db.models import Q
from django.utils.html import format_html
from django import urls


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
    list_display = ('shop_name', 'nick_name', 'location', 'country_code', 'phone_number',
                    'added_by', 'region', 'created_at', 'updated_at')
    fields = ('shop_name', 'nick_name', 'location', ('country_code', 'phone_number'), 'region')
    list_filter = ('country_code', 'region', 'added_by', 'created_at')
    autocomplete_fields = ('region',)
    search_fields = ('shop_name', 'nick_name')
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


class CustomerShopNameFilter(InputFilter):
    parameter_name = 'customer_shop_name'
    title = 'Customer Shop Name'

    def queryset(self, request, queryset):
        if self.value() is not None:
            name = self.value()
            return queryset.filter(
                Q(customer__shop_name=name)
            )
        return queryset


class CustomerNickNameFilter(InputFilter):
    parameter_name = 'customer_nick_name'
    title = 'Customer Nick Name'

    def queryset(self, request, queryset):
        if self.value() is not None:
            name = self.value()
            return queryset.filter(
                Q(customer__nick_name=name)
            )
        return queryset


class SalesAdmin(admin.ModelAdmin):
    list_per_page = 50
    list_filter = (CustomerShopNameFilter, CustomerNickNameFilter, 'served_by', 'date')
    date_hierarchy = 'date'
    list_display = ('customer', 'served_by', 'date', 'get_receipt_url')
    exclude = ('customer', 'served_by', 'date')
    search_fields = ('customer__name',)

    def has_add_permission(self, request):
        return False

    def get_receipt_url(self, obj):
        return format_html('<a class="button" href="{}">view receipt</a>', urls.reverse('receipt', args=[obj.pk]))

    def has_delete_permission(self, request, obj=None):
        return False

    get_receipt_url.short_description = 'Receipt'
    get_receipt_url.allow_tags = True


# Register your models here.
admin.site.register(models.Region, RegionAdmin)
admin.site.register(models.Customer, CustomerAdmin)
admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.SalesCrate)
admin.site.register(models.CreditSettlement)
admin.site.register(models.OverPayOrUnderPay)
admin.site.register(models.ReturnsOrRejects)
admin.site.register(models.Receipt, SalesAdmin)
