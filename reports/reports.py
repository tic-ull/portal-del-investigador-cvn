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

from abc import ABCMeta
import os
import logging
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings as st
from cvn import settings as st_cvn
from cvn.models import (Articulo, Libro, Capitulo, Congreso, Proyecto,
                        Convenio, TesisDoctoral, Patente)
from core.models import UserProfile
from core.ws_utils import CachedWS as ws

logger = logging.getLogger(__name__)


class BaseReport:

    __metaclass__ = ABCMeta

    report_type = None

    def __init__(self, generator_cls, year):
        self.year = year
        self.generator = generator_cls(self.year, self.report_type)

    def get_all_units(self):
        # Override this if you want to call create_reports with empty units
        return []

    def get_investigadores(self, unit, title):
        return NotImplemented

    def create_reports(self, units=None):
        if units is None:
            units = self.get_all_units()
        for unit in units:
            self.create_report(unit)

    def create_report(self, unit=None, title=None):
        inv, profiles, unit_name = self.get_investigadores(unit, title)
        if not inv:
            return
        articulos = Articulo.objects.byUsuariosYear(profiles, self.year)
        libros = Libro.objects.byUsuariosYear(profiles, self.year)
        capitulos_libro = Capitulo.objects.byUsuariosYear(profiles, self.year)
        congresos = Congreso.objects.byUsuariosYear(profiles, self.year)
        proyectos = Proyecto.objects.byUsuariosYear(profiles, self.year)
        convenios = Convenio.objects.byUsuariosYear(profiles, self.year)
        tesis = TesisDoctoral.objects.byUsuariosYear(profiles, self.year)
        patentes = Patente.objects.byUsuariosYear(profiles, self.year)
        return self.generator.go(unit_name, inv,articulos, libros,
                                 capitulos_libro, congresos, proyectos,
                                 convenios, tesis, patentes)

    def get_full_path(self, unit=None):
        if unit != None:
            unit_name = self.get_investigadores(unit, None)[2]
        else:
            unit_name = None
        return os.path.join(
            self.generator.get_save_path(self.year, self.report_type),
            self.generator.get_filename(self.year, unit_name, self.report_type)
        )


class UsersReport(BaseReport):

    report_type = st_cvn.REPORTS_DIRECTORY.USERS.value

    def get_investigadores(self, unit, title):
        if unit is None:
            profiles = UserProfile.objects.all()
        else:
            profiles = UserProfile.objects.filter(documento__in=unit)
            nonexistent_users = list(set(unit) - set([p.documento for p in profiles]))
            if nonexistent_users:
                logger.warn(u"No se encuentran los siguientes usuarios: "
                            + str(nonexistent_users))
        investigadores = [{'cod_persona__nombre': p.user.first_name,
                           'cod_persona__apellido1': p.user.last_name,
                           'cod_persona__apellido2': '',
                           'cod_cce__descripcion': ''}
                          for p in profiles]
        if title is None:
            title = ';'.join(unit)
        return investigadores, profiles, title


class UnitReport(BaseReport):

    WS_URL_ALL = None
    WS_URL_DETAIL = None

    @classmethod
    def get_all_units_names(cls, year=None):
        ws_url = cls.WS_URL_ALL
        if year:
            ws_url += '?year=' + str(year)
        units = ws.get(ws_url)
        return {unit['codigo']: unit['nombre'] for unit in units}

    def get_all_units(self):
        # Save unit names bc the ws doesn't return it when there are no members
        self.unit_names = self.get_all_units_names()
        return self.unit_names.keys()

    def get_investigadores(self, unit, title):
        if unit is None:
            return NotImplemented
        unit_content = ws.get(self.WS_URL_DETAIL % (unit, self.year))[0]
        if unit_content["unidad"] == {}:
            try:
                unit_name = self.unit_names[unit]
            except (AttributeError, KeyError):
                unit_name = unicode(unit)
            logger.warn(u"La unidad " + unit_name
                        + u" no tiene información en " + unicode(self.year))
            return [], [], unit_name
        investigadores = []
        usuarios = []
        for inv in unit_content['miembros']:
            inv = self.check_inves(inv)
            investigadores.append(inv)
            try:
                user = UserProfile.objects.get(rrhh_code=inv['cod_persona'])
                usuarios.append(user)
            except ObjectDoesNotExist:
                pass
        if title is None:
            title = unit_content['unidad']['nombre']
        return investigadores, usuarios, title

    @staticmethod
    def check_inves(inv):
        if 'cod_persona__nombre' not in inv:
            inv['cod_persona__nombre'] = ''
        if 'cod_persona__apellido1' not in inv:
            inv['cod_persona__apellido1'] = ''
        if 'cod_persona__apellido2' not in inv:
            inv['cod_persona__apellido2'] = ''
        if 'cod_cce__descripcion' not in inv:
            inv['cod_cce_descripcion'] = ''
        return inv


class DeptReport(UnitReport):
    report_type = st_cvn.REPORTS_DIRECTORY.DEPT.value
    WS_URL_ALL = st.WS_DEPARTMENTS_ALL
    WS_URL_DETAIL = st.WS_DEPARTMENTS_AND_MEMBERS_UNIT_YEAR


class AreaReport(UnitReport):
    report_type = st_cvn.REPORTS_DIRECTORY.AREA.value
    WS_URL_ALL = st.WS_AREAS_ALL
    WS_URL_DETAIL = st.WS_AREAS_AND_MEMBERS_UNIT_YEAR