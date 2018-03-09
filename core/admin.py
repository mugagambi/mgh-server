from django.contrib.admin import AdminSite
from django.contrib import admin
from core import models
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from utils import admin_link
from django.contrib.auth.models import Group


class CustomAdminSite(AdminSite):
    empty_value_display = '-'
    site_header = "Meru Greens Horticulture Ltd"
    site_title = "Meru Greens Horticulture Ltd Admin Portal"
    index_title = "Welcome to admin portal"

    def get_app_list(self, request):
        """
            Return a sorted list of all the installed apps that have been
            registered in this site.
        """
        ordering = {
            "Users": 1,
            "Crate types": 2,
            "Crates": 3,
            "Products": 4,
            "Aggregation Centers": 5,
            "Regions": 6,
            "Customers": 7,
            "Customer prices": 8,
            "Customer discounts": 9,
            "Orders": 10,
            "Sales": 11,
            "Invoices": 12,
            "Sales crates": 13,
            "Credit settlements": 14,
            "Over pays": 15,
            "Returns or rejectss": 16,
            "Outwards Stocks Summary": 17,
            "Groups": 18

        }
        app_dict = self._build_app_dict(request)
        # a.sort(key=lambda x: b.index(x[0]))
        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: ordering[x['name']])

        return app_list


custom_admin_site = CustomAdminSite(name='custom_admin_site')


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
    list_display = ('number', 'type_link', 'procurement_date')
    list_per_page = 20
    list_filter = ('type', 'procurement_date')
    search_fields = ('number',)
    date_hierarchy = 'procurement_date'
    autocomplete_fields = ('type',)
    list_select_related = True

    @admin_link('type', 'Type')
    def type_link(self, type):
        return type


# Register your models here.
custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register(models.User, UserAdmin)
custom_admin_site.register(models.AggregationCenter, AggregationCenterAdmin)
custom_admin_site.register(models.Product, ProductAdmin)
custom_admin_site.register(models.CrateType, CrateTypeAdmin)
custom_admin_site.register(models.Crate, CrateAdmin)
