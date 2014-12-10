# -*- encoding: UTF-8 -*-

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _
from forms import UploadCVNForm
from models import CVN
from statistics.models import Department
from statistics import settings as st_stat
from utils import scientific_production_to_context, cvn_to_context
from cvn import settings as st_cvn


@login_required
def index(request):
    context = {}
    user = request.user

    dept, dept_json = None, None
    if 'dept' and 'dept_json' in request.session:
        dept = Department.objects.get(name=request.session['dept'])
        dept_json = request.session['dept_json']
        context['department'] = dept
        context['validPercentCVN'] = st_stat.PERCENT_VALID_DEPT_CVN

    try:
        cvn = CVN.objects.get(user_profile__user=user)
        old_cvn_status = cvn.status
    except ObjectDoesNotExist:
        cvn = None
        old_cvn_status = None

    form = UploadCVNForm()
    if request.method == 'POST':
        form = UploadCVNForm(request.POST, request.FILES,
                             user=user, instance=cvn)
        if form.is_valid():
            cvn = form.save()
            context['message'] = _(u'CVN actualizado con éxito.')
            if dept is not None and old_cvn_status != cvn.status:
                dept.update(dept_json['unidad']['nombre'],
                            dept_json['miembros'], commit=True)

    context['form'] = form
    cvn_to_context(user.profile, context)
    context['CVN'] = scientific_production_to_context(user.profile, context)
    context['TIME_WAITING'] = st_cvn.TIME_WAITING
    context['MESSAGES_WAITING'] = st_cvn.MESSAGES_WAITING
    return render(request, 'cvn/index.html', context)


@login_required
def download_cvn(request):
    cvn = request.user.profile.cvn
    pdf = open(cvn.cvn_file.path)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=%s' % (
        cvn.cvn_file.name.split('/')[-1])
    return response


@login_required
@staff_member_required
def ull_report(request):
    context = {}
    user = User.objects.using('historica').get(username='GesInv-ULL')
    scientific_production_to_context(user.profile, context)
    try:
        context['report_date'] = user.profile.cvn.fecha.year - 1
    except ObjectDoesNotExist:
        context['report_date'] = _('No disponible')
    return render(request, 'cvn/ull_report.html', context)
