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

from django.core.management.base import BaseCommand
from cvn.models import CVN


class Command(BaseCommand):
    help = u'Insertar todos los CVN'

    def handle(self, *args, **options):
        try:
            for cvn in CVN.objects.filter(is_inserted=False):
                cvn.remove_producciones()
                cvn.insert_xml()
        except Exception as e:
            print '%s (%s)' % (e.message, type(e))
