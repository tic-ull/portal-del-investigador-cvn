# -*- encoding: UTF-8 -*-

#
#    Copyright 2015
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

# from cvn import settings as st_cvn
# from cvn.fecyt import pdf2xml
from cvn.models import CVN
from cvn.parsers.read_helpers import parse_nif
from django.core.management.base import BaseCommand
from lxml import etree


class Command(BaseCommand):
    help = u'Checks the validity of the files of a CVN'

    def handle(self, *args, **options):
        for cvn in CVN.objects.all():
            try:
                cvn.cvn_file.open()
                # (xml, error) = pdf2xml(cvn.cvn_file.read(), cvn.cvn_file.name)
                cvn.cvn_file.close()
                # if not xml:
                #     print cvn.cvn_file
                #     print st_cvn.ERROR_CODES[error]
            except:
                print cvn.cvn_file
            try:
                cvn.xml_file.open()
                xml_tree = etree.parse(cvn.xml_file)
                cvn.xml_file.seek(0)
                parse_nif(xml_tree)
                cvn.xml_file.close()
            except:
                print cvn.xml_file
