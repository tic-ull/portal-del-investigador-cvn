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
from django.core.management.base import BaseCommand
from optparse import make_option
from cvn.models import CVN
from statistics.models import Area, Department
from cvn.reports.shortcuts import get_report_instance


class Command(BaseCommand):
    help = u'Insertar todos los CVN'
    option_list = BaseCommand.option_list + (
        make_option(
            "-u",
            "--update-all",
            dest="update",
            default=False,
            action="store_true",
            help="Specify if all the reports should be regenerated or just the"
                 " ones with productions from the users that have new CVNs"
        ),
    )

    def create_unit_reports(self, Unit, unit_type, rrhh_codes=None):
        uniq = lambda x: list(set(x))
        units = (uniq([Unit.get_user_unit(code)[0].code for code in rrhh_codes])
                 if rrhh_codes else None)
        year = datetime.date.today().year
        if rrhh_codes != []:
            get_report_instance(unit_type, 'icsv', year).create_reports(units)
            get_report_instance(unit_type, 'ipdf', year).create_reports(units)
            get_report_instance(unit_type, 'rcsv', year).create_reports()

    def handle(self, *args, **options):
        try:
            cvns = CVN.objects.filter(is_inserted=False)
            for cvn in cvns:
                cvn.remove_producciones()
                cvn.insert_xml()
            rrhh_codes = ([cvn.user_profile.rrhh_code for cvn in cvns]
                          if not options['update'] else None)
            self.create_unit_reports(Department, 'ws_dept', rrhh_codes)
            self.create_unit_reports(Area, 'ws_area', rrhh_codes)

        except Exception as e:
            print '%s (%s)' % (e.message, type(e))
