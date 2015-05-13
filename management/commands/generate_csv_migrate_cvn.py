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

from cvn.models import CVN
from cvn.settings import MIGRATION_ROOT
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from django.conf import settings as st
import unicodecsv as csv
import os
import shutil


class Command(BaseCommand):
    help = 'Generate CSV file to migrate users and their CVNs'

    option_list = BaseCommand.option_list + (
        make_option(
            "-d",
            "--date",
            dest="creation_date",
            help="Specify the creation date in format dd-mm-yyyy"
        ),
    )

    def check_args(self, options):
        if options['creation_date'] is None:
            raise CommandError(
                'Option --date="<dd-mm-yyyy>" must be specified.')
        try:
            creation_date = datetime.strptime(
                options['creation_date'], '%d-%m-%Y')
        except ValueError as e:
            raise CommandError(e)
        return creation_date

    def handle(self, *args, **options):
        creation_date = self.check_args(options)
        cvn_path = os.path.join(MIGRATION_ROOT, 'cvn')
        if not os.path.isdir(cvn_path):
            os.makedirs(cvn_path)
        csv_file = csv.writer(
            open(os.path.join(MIGRATION_ROOT, 'users_to_migrate.csv'), 'wb'),
            dialect=st.CSV_DIALECT)
        lines = 0
        for cvn in CVN.objects.filter(uploaded_at__gte=creation_date):
            lines += 1
            try:
                filename = cvn.cvn_file.name.split('/')[-1]
                pdf_path = 'cvn/' + filename
                output = MIGRATION_ROOT + '/' + pdf_path
                shutil.copyfile(
                    cvn.cvn_file.path, output)
                csv_file.writerow([
                    cvn.user_profile.user.username,
                    cvn.user_profile.documento,
                    pdf_path,
                    cvn.user_profile.user.first_name.upper(),
                    cvn.user_profile.user.last_name.upper()])
                print u'[%s] Usuario: %s - CVN: %s \t \t OK' % (
                    lines,
                    cvn.user_profile.user.username,
                    cvn.cvn_file.name)
            except Exception as e:
                print u'[%s] \t \t ERROR: Usuario no insertado (%s - %s)' % (
                    lines,
                    cvn.user_profile.user.username,
                    cvn.cvn_file.name)
                print e
