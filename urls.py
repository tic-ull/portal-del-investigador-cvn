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

from django.conf.urls import patterns, url
from django.http import HttpResponse
from .settings import UNIVERSITY_REPORT_DB
from .views import AdminReportsView, DownloadReportView, ReportsView
import views

urlpatterns = patterns(
    'cvn.views',
    url(r'^$', 'index', name='cvn'),
    url(r'^ull_report/$', views.university_report,
        {'year': UNIVERSITY_REPORT_DB}, name='ull_report'),
    url(r'^download/$', 'download_cvn', name='download_cvn'),
    url(r'^waiting/$', lambda r: HttpResponse(status=204), name='waiting'),
    url(r'^export_data/$', 'export_data_ull', name='export_data_ull'),
    url(r'^reports/$', ReportsView.as_view(), name='reports'),
    url(r'^admin_reports/$', AdminReportsView.as_view(), name='admin_reports'),
    url((r'^reports/(?P<type>\w+)/'
         r'(?P<code>[0-9]+)/(?P<year>[0-9]{4})/(?P<unit_type>\w+)$'),
        DownloadReportView.as_view(), name='download_report'),
    url(r'^reports/(?P<type>rcsv)/(?P<year>[0-9]{4})/(?P<unit_type>\w+)$',
        DownloadReportView.as_view(), name='download_report'),
)
