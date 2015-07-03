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

from cvn.utils import isdigit
from django.core.management.base import BaseCommand, CommandError
from cvn.reports.generators import ResumenCSV
from cvn.reports.generators import InformePDF
from cvn.reports.generators import InformeCSV
from cvn.reports.reports import DeptReport, AreaReport, UsersReport
from optparse import make_option


class Command(BaseCommand):
    help = u'Genera un PDF/CSV con los datos de un Departamento/Area'
    option_list = BaseCommand.option_list + (
        make_option(
            "-y",
            "--year",
            dest="year",
            help="Specify the year in format YYYY",
        ),
        make_option(
            "-u",
            "--unit_code",
            dest="unit_code",
            help="Source unit (department or area) code. Only for -t=a or -t=d",
        ),
        make_option(
            "-l",
            "--user_list",
            dest="user_list",
            help="Source user list (comma separated NIFs). Only for -t=u",
        ),
        make_option(
            "-t",
            "--type",
            dest="type",
            default='d',
            help="Type of filtering: d (department), a (area) or u (user list)",
        ),
        make_option(
            "-f",
            "--format",
            dest="format",
            default='pdf',
            help="Specify the output format: ipdf, icsv, rcsv",
        ),
        make_option(
            "--title",
            dest="title",
            default=u'Producción científica',
            help="Specify a name for the report",
        ),
    )

    def handle(self, *args, **options):
        self.check_args(options)
        year = int(options['year'])
        if options['format'] == 'ipdf':
            Generator = InformePDF
        elif options['format'] == 'icsv':
            Generator = InformeCSV
        else:
            Generator = ResumenCSV
        if options['type'] in ['a', 'd']:
            unit_id = [int(options['unit_code'])] if type(options['unit_code']) is str else None
            if options['type'] == 'a':
                Report = AreaReport
            else:
                Report = DeptReport
            report = Report(Generator, year)
            report.create_reports(unit_id)
        else:
            if not options["user_list"]:
                nifs = None
            else:
                nifs = options["user_list"].split(",")
            report = UsersReport(Generator, int(options['year']))
            report.create_report(nifs, options['title'])

    def check_args(self, options):

        if not isdigit(options['year']):
            raise CommandError(
                "Option `--year=YYYY` must exist and be a number")
        if options['unit_code'] is not None:
            if not isdigit(options['unit_code']):
                raise CommandError("Option `--unit_code=X` must be a number")
        if not options['type'] in ['a', 'd', 'u']:
            raise CommandError("Option `--type=X` must be a (area),"
                               " d (department) or u (user list)")
        if not options['format'] in ['ipdf', 'icsv', 'rcsv']:
            raise CommandError("Option `--format=X` must be ipdf, icsv or rcsv")

        if options['type'] in ['a', 'd'] and options['user_list'] is not None:
            raise CommandError("You can't provide a user list for this type")

        if options['type'] == 'u' and options['unit_code'] is not None:
            raise CommandError("You can't provide a unit code for this type")
