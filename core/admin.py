from django.contrib import admin
from core import models
from django.contrib.auth.admin import UserAdmin


class ProductInline(admin.TabularInline):
    model = models.AggregationCenterProduct
    extra = 1
    can_delete = True
    verbose_name_plural = 'Products'
    verbose_name = 'Product'
    show_change_link = True
    show_full_result_count = True
    autocomplete_fields = ['product']


class AggregationCenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name', 'location')
    inlines = [ProductInline]
    list_per_page = 20


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_per_page = 20


# Register your models here.
admin.site.register(models.User, UserAdmin)
admin.site.register(models.AggregationCenter, AggregationCenterAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.CrateType)
admin.site.register(models.Crate)
admin.site.register(models.Grade)
admin.site.site_title = 'Meru Greens Horticulture Ltd'
admin.site.index_title = 'System Administration'
admin.site.site_header = 'Meru Greens Horticulture Ltd'
admin.site.empty_value_display = '-'
