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

import os
from cvn.reports import DeptReport, AreaReport
from cvn.reports.generators import InformeCSV, InformePDF, ResumenCSV
from django.core.exceptions import ObjectDoesNotExist

_report_type_dict = {'ipdf': InformePDF,
                     'icsv': InformeCSV,
                     'rcsv': ResumenCSV}

_unit_type_dict = {'dept': DeptReport,
                   'area': AreaReport}


def get_report_instance(unit_type, report_type, year):
    Report = _unit_type_dict[unit_type]
    Generator = _report_type_dict[report_type]
    return Report(Generator, year)


def get_report_path(unit_type, report_type, year, code, check_file=True):
    Report = _unit_type_dict[unit_type]
    Generator = _report_type_dict[report_type]
    try:
        team_name = Report.get_unit_name(code, year) if code is not None else None
    except ObjectDoesNotExist:
        raise ReportDoesNotExist
    model_type = Report.report_type
    path = os.path.join(Generator.get_save_path(year, model_type),
                        Generator.get_filename(year, team_name, model_type))
    if check_file and not os.path.isfile(path):
        raise ReportDoesNotExist
    return path


class ReportDoesNotExist(Exception):
    pass