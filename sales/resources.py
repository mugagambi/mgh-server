from import_export import resources
from import_export.fields import Field

from sales import models


class CustomerResource(resources.ModelResource):
    region = Field()
    added_by = Field(column_name='added_by')

    class Meta:
        model = models.Customer
        export_order = ('number', 'shop_name', 'nick_name', 'location', 'phone_number', 'email',
                        'region', 'added_by', 'created_at', 'updated_at')

    def dehydrate_region(self, customer):
        return str(customer.region.name)

    def dehydrate_added_by(self, customer):
        return str(customer.added_by)
