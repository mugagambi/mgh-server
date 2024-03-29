import datetime
import random
from pathlib import Path
from urllib.parse import urlencode

from django.contrib import admin
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import format_html
from weasyprint import HTML


def admin_change_url(obj):
    app_label = obj._meta.app_label
    model_name = obj._meta.model.__name__.lower()
    return reverse('admin:{}_{}_change'.format(
        app_label, model_name
    ), args=(obj.pk,))


def admin_link(attr, short_description, empty_description="-"):
    """Decorator used for rendering a link to a related model in
    the admin detail page.
    attr (str):
        Name of the related field.
    short_description (str):
        Name if the field.
    empty_description (str):
        Value to display if the related field is None.
    The wrapped method receives the related object and should
    return the link text.
    Usage:
        @admin_link('credit_card', _('Credit Card'))
        def credit_card_link(self, credit_card):
            return credit_card.name
    """

    def wrap(func):
        def field_func(self, obj):
            related_obj = getattr(obj, attr)
            if related_obj is None:
                return empty_description
            url = admin_change_url(related_obj)
            return format_html(
                '<a href="{}">{}</a>',
                url,
                func(self, related_obj)
            )

        field_func.short_description = short_description
        field_func.allow_tags = True
        return field_func

    return wrap


def admin_changelist_url(model):
    app_label = model._meta.app_label
    model_name = model.__name__.lower()
    return reverse('admin:{}_{}_changelist'.format(
        app_label,
        model_name)
    )


def admin_changelist_link(
        attr,
        short_description,
        empty_description="-",
        query_string=None
):
    """Decorator used for rendering a link to the list display of
    a related model in the admin detail page.
    attr (str):
        Name of the related field.
    short_description (str):
        Field display name.
    empty_description (str):
        Value to display if the related field is None.
    query_string (function):
        Optional callback for adding a query string to the link.
        Receives the object and should return a query string.
    The wrapped method receives the related object and
    should return the link text.
    Usage:
        @admin_changelist_link('credit_card', _('Credit Card'))
        def credit_card_link(self, credit_card):
            return credit_card.name
    """

    def wrap(func):
        def field_func(self, obj):
            related_obj = getattr(obj, attr)
            if related_obj is None:
                return empty_description
            url = admin_changelist_url(related_obj.model)
            if query_string:
                url += '?' + query_string(obj)
            return format_html(
                '<a href="{}">{}</a>',
                url,
                func(self, related_obj)
            )

        field_func.short_description = short_description
        field_func.allow_tags = True
        return field_func

    return wrap


class DefaultFilterMixin:
    def get_default_filters(self, request):
        """Set default filters to the page.
            request (Request)
            Returns (dict):
                Default filter to encode.
        """
        raise NotImplementedError()


def changelist_view(self, request, extra_context=None):
    ref = request.META.get('HTTP_REFERER', '')
    path = request.META.get('PATH_INFO', '')
    # If already have query parameters or if the page
    # was referred from it self (by drilldown or redirect)
    # don't apply default filter.
    if request.GET or ref.endswith(path):
        return super().changelist_view(
            request,
            extra_context=extra_context
        )
    query = urlencode(self.get_default_filters(request))
    return redirect('{}?{}'.format(path, query))


class InputFilter(admin.SimpleListFilter):
    template = 'admin/input_filter.html'

    def lookups(self, request, model_admin):
        # Dummy, required to show the filter.
        return ((),)

    def choices(self, changelist):
        print(changelist)
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice


def generate_unique_id(id):
    current_time = datetime.datetime.now().time()
    sqstring = '1234567890AQWERTYUIOPSDFGHJKLZXCVBNM' + str(current_time)
    sqlist = list(sqstring)
    random.shuffle(sqlist)
    sqstring = str(sqlist).replace(':', '').replace('\'', '').replace(',', '').replace(' ', '').replace('.', ''). \
        replace('[', '').replace(']', '')
    return sqstring[:6] + str(id)


def main_generate_unique_id():
    current_time = datetime.datetime.now().time()
    sqstring = '1234567890AQWERTYUIOPSDFGHJKLZXCVBNM' + str(current_time)
    sqlist = list(sqstring)
    random.shuffle(sqlist)
    sqstring = str(sqlist).replace(':', '').replace('\'', '').replace(',', '').replace(' ', '').replace('.', ''). \
        replace('[', '').replace(']', '')
    return sqstring[:10]


def handle_pdf_export(folder: str, filename: str, context: dict, template: str):
    """
    prepare pdf for export
    :param folder:
    :param filename:
    :param context:
    :param template:
    :return: export_pdf()
    """
    file = Path(filename)
    if not file.is_file():
        invoice_string = render_to_string(template, context)
        html = HTML(string=invoice_string)
        html.write_pdf(target='{folder}/{filename}'.format(folder=folder, filename=filename))
    return export_pdf(folder, filename=filename)


def export_pdf(folder: str, filename: str):
    """
    Given a folder and filename, this function exports a the file through http content disposition inline
    :param folder:
    :param filename:
    :return: HttpResponse
    """
    fs = FileSystemStorage(folder)
    with fs.open(filename) as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = "inline; filename='{filename}'".format(filename=filename)
        return response


def get_date_period_in_range(date_0: str, date_1: str):
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    delta = date_1 - date_0
    if 32 > delta.days > 1:
        return 'day'
    return 'month'
