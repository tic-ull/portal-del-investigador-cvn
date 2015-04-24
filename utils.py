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

from cvn import settings as st_cvn
from cvn.parsers.read_helpers import parse_nif
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from lxml import etree

import logging

logger = logging.getLogger('cvn')


def cvn_to_context(user, context):
    try:
        cvn = user.cvn
    except ObjectDoesNotExist:
        return
    try:
        # FIXME: Puts the CVN in the context just if the pdf file exists
        cvn.cvn_file.open()
        cvn.xml_file.open()
    except IOError as e:
        logger.error(str(e))
        return
    if cvn.status == st_cvn.CVNStatus.INVALID_IDENTITY:
        xml_tree = etree.parse(cvn.xml_file)
        cvn.xml_file.seek(0)
        nif = parse_nif(xml_tree)
        cvn.xml_file.close()
        if nif is not '':
            context['nif_invalid'] = nif.upper()
    context['cvn'] = cvn
    context['cvn_status'] = st_cvn.CVN_STATUS[cvn.status][1]


def scientific_production_to_context(user_profile, context):
    try:
        if not user_profile.cvn.is_inserted:
            return False
    except ObjectDoesNotExist:
        return False
    context['Articulos'] = user_profile.articulo_set.all()
    context['Capitulos'] = user_profile.capitulo_set.all()
    context['Libros'] = user_profile.libro_set.all()
    context['Congresos'] = user_profile.congreso_set.all()
    context['Proyectos'] = user_profile.proyecto_set.all()
    context['Convenios'] = user_profile.convenio_set.all()
    context['TesisDoctorales'] = user_profile.tesisdoctoral_set.all()
    context['Patentes'] = user_profile.patente_set.all()
    return True


def stats_to_context(request, context):
    """Fills context with info from stats"""
    try:
        from statistics.models import Department, Area
        from statistics import settings as st_stat
    except ImportError:
        pass
    else:
        context['validPercentCVN'] = st_stat.PERCENTAGE_VALID_CVN
        if 'dept_code' in request.session:
            try:
                dept = Department.objects.get(
                    code=request.session['dept_code'])
                context['department'] = dept
                context['label_dept'] = _(u'Departamento')
            except ObjectDoesNotExist:
                pass
        if 'area_code' in request.session:
            try:
                area = Area.objects.get(code=request.session['area_code'])
                context['area'] = area
                context['label_area'] = _(u'Área')
            except ObjectDoesNotExist:
                pass


def isdigit(obj):
    if type(obj) is str and obj.isdigit():
        return True
    else:
        return False
