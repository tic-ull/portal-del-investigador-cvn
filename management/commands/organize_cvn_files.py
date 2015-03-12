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
from django.conf import settings as st
from django.core.files.move import file_move_safe
from django.core.management.base import BaseCommand
from cvn.helpers import get_cvn_path

import os


class Command(BaseCommand):
    help = u'Reorganiza la ubicación de los CVN-PDF'

    def handle(self, *args, **options):
        for cvn in CVN.objects.all():
            try:
                filename = u'CVN-%s.pdf' % cvn.user_profile.documento
                pdf_path = get_cvn_path(cvn, filename)
                new_pdf_path = os.path.join(st.MEDIA_ROOT, pdf_path)

                filename = u'CVN-%s.xml' % cvn.user_profile.documento
                xml_path = get_cvn_path(cvn, filename)
                new_xml_path = os.path.join(st.MEDIA_ROOT, xml_path)

                root_path = '/'.join(new_pdf_path.split('/')[:-1])
                if not os.path.isdir(root_path):
                    os.makedirs(root_path)

                if cvn.cvn_file.path != new_pdf_path:
                    file_move_safe(
                        cvn.cvn_file.path, new_pdf_path, allow_overwrite=True)
                    cvn.cvn_file.name = pdf_path

                if cvn.xml_file.path != new_xml_path:
                    file_move_safe(
                        cvn.xml_file.path, new_xml_path, allow_overwrite=True)
                    cvn.xml_file.name = xml_path

                cvn.save()
            except Exception as e:
                print 'User: %s - CVN: %s' % (
                    cvn.user_profile.user, cvn.cvn_file)
                print '%s (%s)' % (e.message, type(e))
