# -*- encoding: UTF-8 -*-

#
#    Copyright 2014-2015
#
#      STIC-Investigación - Universidad de La Laguna (ULL) <gesinv@ull.edu.es>
#
#    This file is part of CVN.
#
#    CVN is free software: you can redistribute it and/or modify it under
#    the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    CVN is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with CVN.  If not, see
#    <http://www.gnu.org/licenses/>.
#

import datetime
from django.conf import settings as st
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView, View
from cvn import settings as st_cvn
from . import signals
from .forms import UploadCVNForm, GetDataCVNULL
from .models import CVN
from .utils import (scientific_production_to_context, cvn_to_context,
                    stats_to_context)
from .reports import DeptReport, AreaReport


@login_required
def index(request):
    context = {}
    user = request.user
    try:
        cvn = CVN.objects.get(user_profile__user=user)
    except ObjectDoesNotExist:
        cvn = None

    form = UploadCVNForm()
    if request.method == 'POST':
        form = UploadCVNForm(request.POST, request.FILES,
                             user=user, instance=cvn)
        if form.is_valid():
            cvn = form.save()
            context['message'] = _(u'CVN actualizado con éxito.')
            signals.cvn_uploaded.send(sender=None, cvn=cvn)
    context['form'] = form
    stats_to_context(request, context)
    cvn_to_context(user.profile, context)
    context['CVN'] = scientific_production_to_context(user.profile, context)
    context['TIME_WAITING'] = st_cvn.TIME_WAITING
    context['MESSAGES_WAITING'] = st_cvn.MESSAGES_WAITING
    return render(request, 'cvn/index.html', context)


@login_required
def download_cvn(request):
    cvn = request.user.profile.cvn
    try:
        pdf = open(cvn.cvn_file.path)
    except IOError:
        raise Http404
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=%s' % (
        cvn.cvn_file.name.split('/')[-1])
    signals.cvn_downloaded.send(sender=None)
    return response


@login_required
@permission_required('cvn.view_university_report')
def ull_report(request, year):
    if year is None or year not in st.HISTORICAL:
        raise Http404
    context = {}
    user = User.objects.using(st.HISTORICAL[year]).get(username='GesInv-ULL')
    scientific_production_to_context(user.profile, context)
    try:
        context['report_date'] = unicode(year)
    except ObjectDoesNotExist:
        context['report_date'] = _('No disponible')
    return render(request, 'cvn/ull_report.html', context)


@login_required
def export_data_ull(request):
    if not request.user.profile.rrhh_code:
        raise Http404

    context = dict()
    context['form'] = GetDataCVNULL()

    if request.method == 'POST':
        form = GetDataCVNULL(request.POST)
        if form.is_valid():
            start_year = None
            end_year = None

            if 'select_year' in form.data:
                form_year = int(form.data['year'])
                start_year = datetime.date(form_year, 01, 01)
                end_year = datetime.date(form_year, 12, 31)
            if 'range_years' in form.data:
                form_start_year = int(form.data['start_year'])
                start_year = datetime.date(form_start_year, 01, 01)
                end_year = datetime.date(int(form.data['end_year']), 12, 31)

            pdf = CVN.get_user_pdf_ull(request.user, start_year, end_year)

            if not pdf:
                form._errors['__all__'] = _(
                    u'No dispone de información en el periodo seleccionado')
                context['form'] = form
                return render(request, 'cvn/export_data_ull.html', context)

            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = (
                'attachment;' 'filename="CVN-EXPORT-%s.pdf"' % (
                    request.user.profile.documento))
            signals.pdf_exported.send(sender=None)
            return response

        context['form'] = form
    return render(request, 'cvn/export_data_ull.html', context)


class ReportsView(TemplateView):
    template_name = "cvn/reports.html"

    def get_context_data(self, **kwargs):
        context = super(ReportsView, self).get_context_data(**kwargs)
        context['depts'] = DeptReport.get_all_units_names()
        context['areas'] = AreaReport.get_all_units_names()
        return context


class DownloadReportView(View):

    def get(self, request, *args, **kwargs):
        return HttpResponse("Not Implemented Yet")