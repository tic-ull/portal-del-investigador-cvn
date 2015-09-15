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
from django.utils.decorators import method_decorator
from cvn import settings as st_cvn
from . import signals
from .forms import UploadCVNForm, GetDataCVNULL, DownloadReportForm
from .models import CVN
from .utils import (scientific_production_to_context, cvn_to_context,
                    stats_to_context)
from .reports import DeptReport, AreaReport
from .reports.generators import InformeCSV, InformePDF, ResumenCSV
from .decorators import user_can_view_reports
from statistics.models import Area, Department


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
            context['message'] = _("CVN updated successfully.")
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
    response = HttpResponse(pdf, content_type=st.MIMETYPES['pdf'])
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
        context['report_date'] = _("Not Available")
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
                    u'No information in this period')
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


class AdminReportsView(TemplateView):
    template_name = "cvn/reports.html"

    @method_decorator(login_required)
    @method_decorator(user_can_view_reports)
    def dispatch(self, *args, **kwargs):
        return super(AdminReportsView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AdminReportsView, self).get_context_data(**kwargs)
        years = st.HISTORICAL.keys() + [str(datetime.date.today().year)]
        context['depts'] = {}
        context['areas'] = {}
        for year in years:
            context['depts'][year] = DeptReport.get_all_units_names(year=year)
            context['areas'][year] = AreaReport.get_all_units_names(year=year)
        return context

class ReportsView(TemplateView):
    template_name = "cvn/reports.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReportsView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ReportsView, self).get_context_data(**kwargs)
        years = st.HISTORICAL.keys() + [str(datetime.date.today().year)]
        context['depts'] = {}
        context['areas'] = {}
        dc = self.request.session['dept_code']
        ac = self.request.session['area_code']
        for year in years:
            context['depts'][year] = {dc: Department.objects.get(code=dc).name}
            context['areas'][year] = {ac: Area.objects.get(code=ac).name}
        return context


class DownloadReportView(View):

    generator_type = {"ipdf": InformePDF,
                      'icsv': InformeCSV,
                      'rcsv': ResumenCSV}

    report_type = {"dept": DeptReport,
                   "area": AreaReport}

    form_class = DownloadReportForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DownloadReportView, self).dispatch(*args, **kwargs)

    def create_response(self, path):
        try:
            pdf = open(path, 'r')
        except (IOError, TypeError):
            raise Http404
        response = HttpResponse(
            pdf, content_type=st.MIMETYPES[path.split('.')[-1]])
        response['Content-Disposition'] = 'inline; filename=%s' % (
            path.split('/')[-1])
        return response

    def get(self, request, *args, **kwargs):

        # Form validation
        form = self.form_class(kwargs)
        if not form.is_valid():
            raise Http404

        # Get form fields
        params = form.cleaned_data
        unit_type = params['unit_type']
        generator_type = params['type']
        year = int(params['year'])
        code = params['code'] if generator_type != 'rcsv' else None

        # Check user permissions
        user_unit = self.request.session[unit_type + '_code']
        if (not user_can_view_reports(user=self.request.user)
                and user_unit != code):
            raise Http404

        # Generate reports
        Report = self.report_type[unit_type]
        Generator = self.generator_type[generator_type]
        report = Report(Generator, year)
        if year != datetime.date.today().year:
            path = report.get_full_path(code)
        elif generator_type == 'rcsv':
            report.create_reports()
            path = report.get_full_path()
        else:
            path = report.create_report(code)
        response = self.create_response(path)
        return response