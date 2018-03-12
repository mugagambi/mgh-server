from django.contrib import admin
from django.db.models import Sum, Avg

from core.admin import custom_admin_site
from reports import models


# Register your models here.

class SaleSummaryAdmin(admin.ModelAdmin):
    change_list_template = 'admin/sale_summary_change_list.html'
    date_hierarchy = 'receipt__date'
    list_filter = ('receipt__date',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            'total_qty': Sum('qty'),
            'value': Sum('total'),
            'rate': Avg('price')
        }
        response.context_data['summary'] = list(
            qs
                .values('package_product__order_product__product__name')
                .annotate(**metrics)
                .order_by('-value')
        )
        response.context_data['summary_total'] = dict(
            qs.aggregate(**metrics)
        )

        return response


custom_admin_site.register(models.SaleSummary, SaleSummaryAdmin)
