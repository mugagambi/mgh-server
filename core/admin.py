from django.contrib import admin
from core import models
from django.contrib.auth.admin import UserAdmin

# Register your models here.
admin.site.register(models.User, UserAdmin)
admin.site.register(models.AggregationCenter)
admin.site.register(models.Product)
admin.site.register(models.AggregationCenterProduct)
admin.site.register(models.CrateType)
admin.site.register(models.Crate)
admin.site.register(models.Grade)
admin.site.site_title = 'Meru Greens Horticulture Ltd'
admin.site.index_title = 'System Administration'
admin.site.site_header = 'Meru Greens Horticulture Ltd'
