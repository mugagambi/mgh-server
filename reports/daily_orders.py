from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from pytz import timezone as pytz_zone

from reports import forms

AFRICA_NAIROBI = pytz_zone('Africa/Nairobi')


@login_required()
def period(request):
    if request.method == 'POST':
        form = forms.ProductCustomer(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            return redirect('daily_sales_report',
                            date_0=str(date_0), date_1=str(date_1))
    else:
        form = forms.ProductCustomer(initial={'date_0': timezone.datetime.today(),
                                              'date_1': timezone.datetime.today(), })
    return render(request, 'reports/daily_sales/period.html',
                  {'form': form})
