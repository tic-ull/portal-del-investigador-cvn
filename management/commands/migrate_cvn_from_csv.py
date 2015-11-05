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

from core.models import UserProfile
from cvn import settings as st_cvn
from cvn.forms import UploadCVNForm
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from optparse import make_option
from django.conf import settings as st
import unicodecsv as csv
import os
from core.routers import in_database


class Command(BaseCommand):
    help = u'Migración de usuarios con su CVN desde un CSV del viejo portal'

    option_list = BaseCommand.option_list + (
        make_option(
            "--database",
            dest="database",
            help="Specify database to update",
        ),
    )

    def handle(self, *args,  **options):
        database = (options['database']
                    if options['database'] is not None
                    else 'default')
        with in_database(database, write=True):
            cvn_file = os.path.join(st_cvn.MIGRATION_ROOT,
                                    'users_to_migrate.csv')
            with open(cvn_file, 'rb') as csvfile:
                lines = csv.reader(csvfile, dialect=st.CSV_DIALECT)
                for line in lines:
                    user, created = UserProfile.get_or_create_user(
                        username=unicode(line[0]), documento=unicode(line[1]))
                    if created:
                        user.first_name = line[3]
                        user.last_name = line[4]
                        user.save()

                    # Reload user to have profile updated
                    user = User.objects.get(pk=user.profile.user.pk)
                    try:
                        pdf_file = os.path.join(st_cvn.MIGRATION_ROOT, line[2])
                        upload_file = open(pdf_file)
                    except IOError:
                        print (u'[%s] \t \t ERROR: CVN No encontrado (%s - %s)'
                               % (lines.line_num, line[0], line[2]))
                        continue
                    cvn_file = SimpleUploadedFile(
                        upload_file.name,
                        upload_file.read(),
                        content_type="application/pdf")
                    upload_file.close()
                    try:
                        user.profile.cvn.remove()
                        user.profile.cvn.delete()
                    except ObjectDoesNotExist:
                        pass
                    form = UploadCVNForm(initial={'cvn_file': cvn_file},
                                         user=user)
                    if form.is_valid():
                        cvn = form.save()
                        cvn.insert_xml()
                        print u'[%s] Usuario: %s - CVN: %s \t \t OK' % (
                            lines.line_num, line[0], line[2])
                    else:
                        print u'[%s] \t \t ERROR: CVN No válido (%s - %s)' % (
                            lines.line_num, line[0], line[2])
