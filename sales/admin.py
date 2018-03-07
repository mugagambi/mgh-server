from django.contrib import admin
from sales import models
from utils import InputFilter
from django.db.models import Q
from django.utils.html import format_html
from django import urls
from import_export import resources
from import_export.admin import ExportMixin
from import_export.fields import Field
from core.admin import custom_admin_site


class RegionResource(resources.ModelResource):
    class Meta:
        model = models.Region


class RegionAdmin(ExportMixin, admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name',)
    resource_class = RegionResource


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


class CustomerResource(resources.ModelResource):
    region = Field()
    added_by = Field()

    class Meta:
        model = models.Customer

    def dehydrate_region(self, customer):
        return customer.region.name

    def dehydrate_added_by(self, customer):
        return customer.added_by.username


class CustomerAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = CustomerResource
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


class CustomerShopNameFilter(InputFilter):
    parameter_name = 'customer_shop_name'
    title = 'Customer Shop Name'

    def queryset(self, request, queryset):
        if self.value() is not None:
            name = self.value()
            return queryset.filter(
                Q(customer__shop_name__icontains=name)
            )
        return queryset


class CustomerNickNameFilter(InputFilter):
    parameter_name = 'customer_nick_name'
    title = 'Customer Nick Name'

    def queryset(self, request, queryset):
        if self.value() is not None:
            name = self.value()
            return queryset.filter(
                Q(customer__nick_name__icontains=name)
            )
        return queryset


class ProductNameFilter(InputFilter):
    parameter_name = 'product_name'
    title = 'Product Name'

    def queryset(self, request, queryset):
        if self.value() is not None:
            name = self.value()
            return queryset.filter(
                Q(product__name__icontains=name)
            )
        return queryset


class CustomerPriceResource(resources.ModelResource):
    product = Field()

    class Meta:
        model = models.CustomerPrice


class CustomerPricesAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = CustomerPriceResource
    list_display = ('id', 'customer', 'price', 'product', 'created_at', 'updated_at')
    fields = ('customer', 'price', 'product')
    autocomplete_fields = ('customer',)
    date_hierarchy = 'updated_at'
    list_per_page = 50
    list_filter = (CustomerShopNameFilter, CustomerNickNameFilter, ProductNameFilter, 'created_at', 'updated_at')


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


class SalesCustomerShopNameFilter(InputFilter):
    parameter_name = 'customer_shop_name'
    title = 'Customer Shop Name'

    def queryset(self, request, queryset):
        if self.value() is not None:
            name = self.value()
            return queryset.filter(
                Q(customer__shop_name__icontains=name)
            )
        return queryset


class SalesCustomerNickNameFilter(InputFilter):
    parameter_name = 'customer_nick_name'
    title = 'Customer Nick Name'

    def queryset(self, request, queryset):
        if self.value() is not None:
            name = self.value()
            return queryset.filter(
                Q(customer__nick_name__icontains=name)
            )
        return queryset


class SalesAdmin(admin.ModelAdmin):
    list_per_page = 50
    list_filter = (SalesCustomerShopNameFilter, SalesCustomerNickNameFilter, 'served_by', 'date')
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
custom_admin_site.register(models.Region, RegionAdmin)
custom_admin_site.register(models.Customer, CustomerAdmin)
custom_admin_site.register(models.CustomerPrice, CustomerPricesAdmin)
custom_admin_site.register(models.Order, OrderAdmin)
custom_admin_site.register(models.SalesCrate)
custom_admin_site.register(models.CreditSettlement)
custom_admin_site.register(models.OverPayOrUnderPay)
custom_admin_site.register(models.ReturnsOrRejects)
custom_admin_site.register(models.Receipt, SalesAdmin)
