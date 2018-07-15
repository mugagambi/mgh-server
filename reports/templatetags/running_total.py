from django.template.defaultfilters import register


@register.filter
def running_total(deposit_list):
    return sum(d.get('amount__sum') for d in deposit_list)
