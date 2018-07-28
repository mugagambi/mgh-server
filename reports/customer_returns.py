import datetime
from itertools import groupby

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from django.shortcuts import redirect, render
from django.utils import timezone
from pytz import timezone as pytz_zone

from reports import forms
from sales import models

AFRICA_NAIROBI = pytz_zone('Africa/Nairobi')


# todo add the right permissions
@login_required()
def period(request):
    if request.method == 'POST':
        form = forms.SaleSummaryDate(request.POST)
        if form.is_valid():
            date_0 = form.cleaned_data['date_0']
            date_1 = form.cleaned_data['date_1']
            return redirect('customer_returns_report',
                            date_0=date_0, date_1=date_1)
    else:
        form = forms.SaleSummaryDate(initial={'date_0': timezone.datetime.today(),
                                              'date_1': timezone.datetime.today()})
    return render(request, 'reports/customer-returns/period.html',
                  {'form': form})


def report(request, date_0, date_1):
    date_0 = timezone.datetime.strptime(date_0, '%Y-%m-%d').date()
    date_1 = timezone.datetime.strptime(date_1, '%Y-%m-%d').date()
    date_0_datetime = timezone.datetime.combine(date_0, datetime.time(0, 0, tzinfo=AFRICA_NAIROBI))
    date_1_datetime = timezone.datetime.combine(date_1, datetime.time(23, 59, tzinfo=AFRICA_NAIROBI))
    returns = models.Return.objects. \
        filter(date__range=(date_0_datetime, date_1_datetime)). \
        values('product__name', 'reason').annotate(Sum('qty'), credit_note=Sum(F('price') * F('qty'))). \
        order_by('product__name')
    final_returns = []
    for k, v in groupby(returns, key=lambda x: x['product__name']):
        v = list(v)
        final_returns.append({
            'product': k,
            'rotten_qty': sum(d['qty__sum'] if d['reason'] == 'R' else 0 for d in v),
            'rotten_credit': sum(d['credit_note'] if d['reason'] == 'R' else 0 for d in v),
            'unripe_qty': sum(d['qty__sum'] if d['reason'] == 'U' else 0 for d in v),
            'unripe_credit': sum(d['credit_note'] if d['reason'] == 'U' else 0 for d in v),
            'overripe_qty': sum(d['qty__sum'] if d['reason'] == 'O' else 0 for d in v),
            'overripe_credit': sum(d['credit_note'] if d['reason'] == 'O' else 0 for d in v),
            'poor_quality_qty': sum(d['qty__sum'] if d['reason'] == 'P' else 0 for d in v),
            'poor_quality_credit': sum(d['credit_note'] if d['reason'] == 'P' else 0 for d in v),
            'excess_qty': sum(d['qty__sum'] if d['reason'] == 'E' else 0 for d in v),
            'excess_credit': sum(d['credit_note'] if d['reason'] == 'E' else 0 for d in v),
            'total_qty': sum(d['qty__sum'] for d in v),
            'total_credit': sum(d['credit_note'] for d in v),
        })
    rotten_credit = sum(r['rotten_credit'] for r in final_returns)
    unripe_credit = sum(r['unripe_credit'] for r in final_returns)
    overripe_credit = sum(r['overripe_credit'] for r in final_returns)
    poor_quality_credit = sum(r['poor_quality_credit'] for r in final_returns)
    excess_credit = sum(r['excess_credit'] for r in final_returns)
    total_credit = sum(r['total_credit'] for r in final_returns)
    cxt = {'returns': final_returns, 'date_0': date_0_datetime, 'date_1': date_1_datetime,
           'rotten_credit': rotten_credit, 'unripe_credit': unripe_credit, 'overripe_credit': overripe_credit,
           'poor_quality_credit': poor_quality_credit, 'excess_credit': excess_credit, 'total_credit': total_credit}
    return render(request, 'reports/customer-returns/report.html', cxt)
