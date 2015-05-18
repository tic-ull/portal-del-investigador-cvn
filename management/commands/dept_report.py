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
from cvn.reports.reports import DeptReport, AreaReport
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
            "-i",
            "--id",
            dest="id",
            help="Specify the ID of the Department/Area",
        ),
        make_option(
            "-t",
            "--type",
            dest="type",
            default='d',
            help="Specify the type of filtering: d (department) or a (area)",
        ),
        make_option(
            "-f",
            "--format",
            dest="format",
            default='pdf',
            help="Specify the output format",
        ),
    )

    def handle(self, *args, **options):
        self.check_args(options)
        year = int(options['year'])
        unit_id = [int(options['id'])] if type(options['id']) is str else None
        if options['format'] == 'pdf':
            generator_cls = InformePDF
        elif options['format'] == 'icsv':
            generator_cls = InformeCSV
        else:
            generator_cls = ResumenCSV
        if options['type'] == 'a':
            reports_cls = AreaReport
            model_type = 'area'
        else:
            reports_cls = DeptReport
            model_type = 'department'
        generator = generator_cls(year, model_type)
        report = reports_cls(generator)
        report.create_reports(year, unit_id)

    def check_args(self, options):
        if not isdigit(options['year']):
            raise CommandError(
                "Option `--year=YYYY` must exist and be a number")
        if (not isdigit(options['id'])) and options['id'] is not None:
            raise CommandError("Option `--id=X` must be a number")
        if not options['type'] == 'a' and not options['type'] == 'd':
            raise CommandError("Option `--type=X` must be a (area) "
                               "or d (department)")
        f = options['format']
        if not f == 'pdf' and not f == 'csv' and not f == 'icsv':
            raise CommandError("Option `--format=X` must be pdf, csv or icsv")