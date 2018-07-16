from django.template.defaultfilters import register


@register.filter
def running_total(deposit_list):
    return sum(d.get('amount__sum') for d in deposit_list)


@register.filter
def invoice_receipt_total(receipt_list):
    return sum(d.total for d in receipt_list)
