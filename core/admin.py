from django.contrib import admin
from core import models
from django.contrib.auth.admin import UserAdmin


class ProductInline(admin.TabularInline):
    model = models.AggregationCenterProduct
    extra = 1
    can_delete = False
    verbose_name_plural = 'Products'
    verbose_name = 'Product'
    show_change_link = True
    show_full_result_count = True
    autocomplete_fields = ['product']


class AggregationCenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name', 'location')
    exclude = ('is_active',)
    inlines = [ProductInline]
    list_per_page = 20

    def delete_model(self, request, obj):
        obj.is_active = False
        obj.save()

    def get_queryset(self, request):
        return models.AggregationCenter.objects.filter(is_active=True)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_per_page = 20


class CrateTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight')
    list_per_page = 20
    search_fields = ('name',)


class CrateAdmin(admin.ModelAdmin):
    list_display = ('number', 'type', 'procurement_date')
    list_per_page = 20
    list_filter = ('type', 'procurement_date')
    search_fields = ('number',)
    date_hierarchy = 'procurement_date'
    autocomplete_fields = ('type',)


# Register your models here.
admin.site.register(models.User, UserAdmin)
admin.site.register(models.AggregationCenter, AggregationCenterAdmin)
admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.CrateType, CrateTypeAdmin)
admin.site.register(models.Crate, CrateAdmin)
admin.site.site_title = 'Meru Greens Horticulture Ltd'
admin.site.index_title = 'System Administration'
admin.site.site_header = 'Meru Greens Horticulture Ltd'
admin.site.empty_value_display = '-'
