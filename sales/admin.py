from django import urls
from django.contrib import admin
from django.db.models import Q
from django.utils.html import format_html
from import_export import resources
from import_export.admin import ExportMixin
from import_export.fields import Field
from utils import admin_link
from core.admin import custom_admin_site
from sales import models
from utils import InputFilter, generate_unique_id


def generate_unique_number(obj, cls, context, request, form, change):
    if obj.number:
        return super(cls, context).save_model(request, obj, form, change)
    obj.number = generate_unique_id(request.user.id)


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
    phone_number = Field()

    class Meta:
        model = models.Customer

    def dehydrate_region(self, customer):
        return customer.region.name

    def dehydrate_added_by(self, customer):
        return customer.added_by.username

    def dehydrate_phone_number(self, customer):
        return str(customer.phone_number)


class NumberFilter(InputFilter):
    parameter_name = 'number'
    title = 'Number'

    def queryset(self, request, queryset):
        if self.value() is not None:
            number = self.value()
            return queryset.filter(
                Q(number__iexact=number)
            )
        return queryset


class CustomerNumberFilter(NumberFilter):
    title = 'Customer Number'


class CustomerShopNameFilter(InputFilter):
    parameter_name = 'customer_shop_name'
    title = 'Customer Shop Name'

    def queryset(self, request, queryset):
        if self.value() is not None:
            name = self.value()
            return queryset.filter(
                Q(shop_name__icontains=name)
            )
        return queryset


class CustomerNickNameFilter(InputFilter):
    parameter_name = 'customer_nick_name'
    title = 'Customer Nick Name'

    def queryset(self, request, queryset):
        if self.value() is not None:
            name = self.value()
            return queryset.filter(
                Q(nick_name__icontains=name)
            )
        return queryset


class CustomerAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = CustomerResource
    inlines = [CustomerPriceInline, CustomerDiscountInline]
    list_display = ('number', 'shop_name', 'nick_name', 'location', 'get_phone_number',
                    'added_by', 'region_link', 'created_at', 'updated_at')
    fields = ('number', 'shop_name', 'nick_name', 'location', 'phone_number', 'region')
    readonly_fields = ('number',)
    list_filter = (
        CustomerNumberFilter, CustomerShopNameFilter, CustomerNickNameFilter, 'region', 'added_by',
        'created_at')
    autocomplete_fields = ('region',)
    date_hierarchy = 'created_at'
    search_fields = ('number', 'shop_name', 'nick_name')
    list_select_related = True

    def get_phone_number(self, obj):
        return str(obj.phone_number)

    def save_model(self, request, obj, form, change):
        obj.added_by = request.user
        generate_unique_number(obj, CustomerAdmin, self, request, form, change)
        super(CustomerAdmin, self).save_model(request, obj, form, change)

    @admin_link('region', 'Region')
    def region_link(self, region):
        return region

    get_phone_number.short_description = 'Phone Number'
    get_phone_number.admin_order_field = 'phone_number'


class ForeignKeyCustomerShopNameFilter(InputFilter):
    parameter_name = 'customer_shop_name'
    title = 'Customer Shop Name'

    def queryset(self, request, queryset):
        if self.value() is not None:
            name = self.value()
            return queryset.filter(
                Q(customer__shop_name__icontains=name)
            )
        return queryset


class ForeignKeyCustomerNickNameFilter(InputFilter):
    parameter_name = 'customer_nick_name'
    title = 'Customer Nick Name'

    def queryset(self, request, queryset):
        if self.value() is not None:
            name = self.value()
            return queryset.filter(
                Q(customer__nick_name__icontains=name)
            )
        return queryset


class ForeignCustomerNumberFilter(InputFilter):
    parameter_name = 'customer_number'
    title = 'Customer Number'

    def queryset(self, request, queryset):
        if self.value() is not None:
            number = self.value()
            return queryset.filter(
                Q(customer__number__iexact=number)
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
    list_display = ('customer', 'price', 'product_link', 'created_at', 'updated_at')
    fields = ('customer', 'price', 'product')
    autocomplete_fields = ('customer', 'product')
    date_hierarchy = 'updated_at'
    list_per_page = 50
    list_filter = (
        ForeignCustomerNumberFilter, ForeignKeyCustomerShopNameFilter, ForeignKeyCustomerNickNameFilter,
        ProductNameFilter, 'created_at',
        'updated_at')
    list_select_related = True

    @admin_link('product', 'Product')
    def product_link(self, product):
        return product


class CustomerDiscountsResource(resources.ModelResource):
    class Meta:
        model = models.CustomerDiscount


class CustomerDiscountsAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = CustomerDiscountsResource
    list_display = ('customer', 'discount', 'product_link', 'created_at', 'updated_at')
    fields = ('customer', 'discount', 'product')
    autocomplete_fields = ('customer', 'product')
    date_hierarchy = 'updated_at'
    list_per_page = 50
    list_filter = (
        ForeignCustomerNumberFilter, ForeignKeyCustomerShopNameFilter, ForeignKeyCustomerNickNameFilter,
        ProductNameFilter, 'created_at',
        'updated_at')

    @admin_link('product', 'Product')
    def product_link(self, product):
        return product


class OrderProductsInline(admin.TabularInline):
    model = models.OrderProduct
    can_delete = True
    autocomplete_fields = ('product',)
    extra = 1
    verbose_name = 'Item'
    verbose_name_plural = 'Items'


class OrderNumberFilter(NumberFilter):
    title = 'Order Number'


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderProductsInline]
    list_display = ('number', 'customer_link', 'received_by', 'date_delivery', 'created_at', 'updated_at')
    fields = ('number', 'customer', 'date_delivery')
    readonly_fields = ('number',)
    autocomplete_fields = ('customer',)
    list_filter = (
        ForeignCustomerNumberFilter, OrderNumberFilter, ForeignKeyCustomerShopNameFilter,
        ForeignKeyCustomerNickNameFilter, 'received_by', 'date_delivery', 'created_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 20
    list_select_related = True
    search_fields = ('customer__shop_name', 'customer__nick_name', 'number')

    @admin_link('customer', 'Customer')
    def customer_link(self, customer):
        return customer

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if instance.number:
                instance.number = instance.number
                instance.save()
            else:
                instance.number = generate_unique_id(request.user.id)
                instance.save()
        formset.save_m2m()

    def save_model(self, request, obj, form, change):
        obj.received_by = request.user
        generate_unique_number(obj, OrderAdmin, self, request, form, change)
        super(OrderAdmin, self).save_model(request, obj, form, change)


class SalesCrateAdmin(admin.ModelAdmin):
    list_display = ('agent', 'crate', 'date_issued', 'date_returned', 'held_by')
    list_filter = ('agent', 'crate', 'date_issued', 'date_returned', 'held_by')
    list_per_page = 20
    list_select_related = True


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
    list_display = ('customer', 'served_by', 'date')
    search_fields = ('customer__name',)
    list_select_related = True


class InvoiceAdmin(admin.ModelAdmin):
    list_per_page = 50
    list_filter = (SalesCustomerShopNameFilter, SalesCustomerNickNameFilter, 'served_by', 'date')
    date_hierarchy = 'date'
    list_display = ('customer', 'get_credit_amount', 'get_due_date', 'served_by', 'date', 'get_invoice_url')
    exclude = ('customer', 'served_by', 'date')
    search_fields = ('customer__name',)
    list_select_related = True

    def has_add_permission(self, request):
        return False

    def get_invoice_url(self, obj):
        return format_html('<a class="button" href="{}">view invoice</a>', urls.reverse('receipt', args=[obj.pk]))

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return models.Invoices.objects.filter(receiptpayment__type=4)

    def get_credit_amount(self, obj):
        return obj.receiptpayment_set.first().amount

    def get_due_date(self, obj):
        return obj.receiptpayment_set.first().date_to_pay

    get_due_date.short_description = 'Due Date'
    get_credit_amount.short_description = 'Amount (Ksh.)'


class ReceiptNumberFilter(NumberFilter):
    title = 'Receipt Number'




class ReturnAdmin(admin.ModelAdmin):
    pass


class PackageProductInline(admin.TabularInline):
    model = models.PackageProduct
    can_delete = True
    autocomplete_fields = ('order_product',)
    extra = 1
    verbose_name = 'Item'
    verbose_name_plural = 'Items'
    readonly_fields = ('number',)


class PackageAdmin(admin.ModelAdmin):
    inlines = [PackageProductInline]
    list_display = ('number', 'order', 'packaged_by', 'created_at', 'updated_at')
    fields = ('order',)
    list_select_related = True
    readonly_fields = ('number',)
    autocomplete_fields = ('order',)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if instance.number:
                instance.number = instance.number
                instance.save()
            else:
                instance.number = generate_unique_id(request.user.id)
                instance.save()
        formset.save_m2m()

    def save_model(self, request, obj, form, change):
        obj.packaged_by = request.user
        generate_unique_number(obj, PackageAdmin, self, request, form, change)
        super(PackageAdmin, self).save_model(request, obj, form, change)


class OrderProductAdmin(admin.ModelAdmin):
    search_fields = ('order__number', 'product__name')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# Register your models here.
custom_admin_site.register(models.Region, RegionAdmin)
custom_admin_site.register(models.Customer, CustomerAdmin)
custom_admin_site.register(models.CustomerPrice, CustomerPricesAdmin)
custom_admin_site.register(models.CustomerDiscount, CustomerDiscountsAdmin)
custom_admin_site.register(models.Order, OrderAdmin)
custom_admin_site.register(models.SalesCrate)
custom_admin_site.register(models.CreditSettlement)
custom_admin_site.register(models.Return)
custom_admin_site.register(models.Receipt, SalesAdmin)
custom_admin_site.register(models.ReceiptParticular)
custom_admin_site.register(models.ReceiptPayment)
custom_admin_site.register(models.Invoices, InvoiceAdmin)
custom_admin_site.register(models.OrderProduct, OrderProductAdmin)
custom_admin_site.register(models.Package, PackageAdmin)
