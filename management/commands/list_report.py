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

from optparse import make_option
from cvn.utils import isdigit
from django.core.management.base import BaseCommand, CommandError
from cvn.reports.generators import ResumenCSV
from cvn.reports.generators import InformePDF
from cvn.reports.generators import InformeCSV
from cvn.reports.reports import ListReport


class Command(BaseCommand):
    help = u'Genera un PDF/CSV con los datos de una lista de usuarios'
    option_list = BaseCommand.option_list + (
        make_option(
            "-l",
            "--list",
            dest="list",
            default="",
            help="List of NIFs from the users of the report",
        ),
        make_option(
            "-f",
            "--format",
            dest="format",
            default='pdf',
            help="Specify the output format",
        ),
        make_option(
            "-t",
            "--title",
            dest="title",
            default=u'Producción científica',
            help="Specify a name for the list of users",
        ),
        make_option(
            "-y",
            "--year",
            dest="year",
            help="Specify the year in format YYYY",
        ),
    )

    def handle(self, *args, **options):
        self.check_args(options)
        if options['format'] == 'pdf':
            Generator = InformePDF
        elif options['format'] == 'icsv':
            Generator = InformeCSV
        else:
            Generator = ResumenCSV
        nifs = options["list"].split(",")
        report = ListReport(Generator, int(options['year']))
        report.create_report(nifs, options['title'])

    @staticmethod
    def check_args(options):
        f = options['format']
        if not f == 'pdf' and not f == 'csv' and not f == 'icsv':
            raise CommandError("Option `--format=X` must be pdf, csv or icsv")
        if not isdigit(options['year']):
            raise CommandError(
                "Option `--year=YYYY` must exist and be a number")