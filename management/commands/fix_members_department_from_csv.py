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


from cvn.models import ReportMember, ReportDept

from django.core.management.base import BaseCommand
from django.conf import settings as st
import os
import unicodecsv


class Command(BaseCommand):
    help = u'Fix memberships of departments'

    def handle(self, *args, **options):
        with open(os.path.join(st.BASE_DIR,
                               'Investigadores_cambiar_dept_code.csv')) as csv:
            reader = unicodecsv.DictReader(csv, delimiter=',')
            for row in reader:
                member = ReportMember.objects.get(
                    user_profile__rrhh_code=row['COD_PERSONA'])
                departamento = ReportDept.objects.get(code=row[
                    'COD_DEPARTAMENTO'])
                member.department = departamento
                member.save()
