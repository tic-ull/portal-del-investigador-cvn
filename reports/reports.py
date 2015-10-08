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
import logging
import datetime
from django.conf import settings as st
from core.routers import in_database
from cvn import settings as st_cvn
from cvn.models import (Articulo, Libro, Capitulo, Congreso, Proyecto,
                        Convenio, TesisDoctoral, Patente, ReportDept,
                        ReportArea)
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
        # We use the historical cv of the users
        database = (st.HISTORICAL[str(self.year)]
                    if self.year != datetime.date.today().year
                    else 'default')
        with in_database(database):
            articulos = list(Articulo.objects.byUsuariosYear(
                profiles, self.year))
            libros = list(Libro.objects.byUsuariosYear(profiles, self.year))
            capitulos_libro = list(Capitulo.objects.byUsuariosYear(
                profiles, self.year))
            congresos = list(Congreso.objects.byUsuariosYear(
                profiles, self.year))
            proyectos = list(Proyecto.objects.byUsuariosYear(
                profiles, self.year))
            convenios = list(Convenio.objects.byUsuariosYear(
                profiles, self.year))
            tesis = list(TesisDoctoral.objects.byUsuariosYear(
                profiles, self.year))
            patentes = list(Patente.objects.byUsuariosYear(
                profiles, self.year))
        return self.generator.go(unit_name, inv, articulos, libros,
                                 capitulos_libro, congresos, proyectos,
                                 convenios, tesis, patentes)

    @classmethod
    def get_unit_name(cls, code, year):
        return NotImplemented


class UsersReport(BaseReport):
    report_type = st_cvn.REPORTS_DIRECTORY.USERS.value

    def get_investigadores(self, unit, title):
        if unit is None:
            profiles = UserProfile.objects.all()
        else:
            profiles = UserProfile.objects.filter(documento__in=unit)
            nonexistent_users = (
                list(set(unit) - set([p.documento for p in profiles])))
            if nonexistent_users:
                logger.warn(u"No se encuentran los siguientes usuarios: " +
                            str(nonexistent_users))
        investigadores = [{'cod_persona__nombre': p.user.first_name,
                           'cod_persona__apellido1': p.user.last_name,
                           'cod_persona__apellido2': '',
                           'cod_cce__descripcion': ''}
                          for p in profiles]
        if title is None:
            title = ';'.join(unit)
        return investigadores, profiles, title


class DBReport(BaseReport):
    Report = None

    def get_all_units(self):
        with in_database(st.HISTORICAL[str(self.year)]):
            return [r.code for r in self.Report.objects.exclude(
                reportmember=None).order_by('name')]

    def get_investigadores(self, unit, title):
        with in_database(st.HISTORICAL[str(self.year)]):
            unit_model = self.Report.objects.get(code=unit)
            if unit_model is None:
                return NotImplemented
            members = unit_model.reportmember_set.all().order_by(
                'user_profile__user__last_name',
                'user_profile__user__first_name'
            )
            investigadores = []
            usuarios = []
            for m in members:
                usuarios.append(m.user_profile)
                investigadores.append({
                    'cod_persona__nombre': m.user_profile.user.first_name,
                    'cod_persona__apellido1': m.user_profile.user.last_name,
                    'cod_persona__apellido2': '',
                    'cod_cce__descripcion': m.cce
                })

            if title is None:
                title = unit_model.name
            return investigadores, usuarios, title

    @classmethod
    def get_unit_name(cls, code, year):
        with in_database(st.HISTORICAL[str(year)]):
            return cls.Report.objects.get(code=code).name

    @classmethod
    def get_all_units_names(cls, year):
        with in_database(st.HISTORICAL[str(year)]):
            return list(cls.Report.objects.all())


class DBDeptReport(DBReport):
    report_type = st_cvn.REPORTS_DIRECTORY.DEPT.value
    Report = ReportDept


class DBAreaReport(DBReport):
    report_type = st_cvn.REPORTS_DIRECTORY.AREA.value
    Report = ReportArea


class WSReport(BaseReport):

    WS_URL_ALL = None
    WS_URL_DETAIL = None

    @classmethod
    def get_all_units_names(cls, year=None):
        ws_url = cls.WS_URL_ALL
        if year:
            ws_url += '?year=' + str(year)
        units = ws.get(ws_url)
        return [{'code': unit['codigo'], 'name': unit['nombre']} for unit in units]

    def get_all_units(self):
        # Save unit names bc the ws doesn't return it when there are no members
        self.unit_names = self.get_all_units_names(self.year)
        return [unit['code'] for unit in self.unit_names]

    def get_investigadores(self, unit, title):
        if unit is None:
            return NotImplemented
        unit_content = ws.get(self.WS_URL_DETAIL % (unit, self.year))[0]
        if unit_content["unidad"] == {}:
            try:
                unit_name = filter(
                    lambda x: x['code'] == unit, self.unit_names)[0]['name']
            except (AttributeError, KeyError):
                unit_name = unicode(unit)
            logger.warn(u"La unidad " + unit_name
                        + u" no tiene información en " + unicode(self.year))
            return [], [], unit_name
        investigadores = []
        usuarios = []
        for inv in unit_content['miembros']:
            inv = self._check_inves(inv)
            investigadores.append(inv)
            try:
                up = UserProfile.objects.get(rrhh_code=inv['cod_persona'])
            except UserProfile.DoesNotExist:
                response = ws.get(st.WS_DOCUMENT % inv['cod_persona'])
                document = response['numero_documento'] + response['letra']
                up = UserProfile.get_or_create_user(document,
                                                    document)[0].profile
                up.rrhh_code = inv['cod_persona']
                up.save()
                up.user.first_name = inv['cod_persona__nombre']
                up.user.last_name = (inv['cod_persona__apellido1'] +
                                     " " +
                                     inv['cod_persona__apellido2'])[:30]
                up.user.save()
            usuarios.append(up)
        if title is None:
            title = unit_content['unidad']['nombre']
        return investigadores, usuarios, title

    @staticmethod
    def _check_inves(inv):
        if 'cod_persona__nombre' not in inv:
            inv['cod_persona__nombre'] = ''
        if 'cod_persona__apellido1' not in inv:
            inv['cod_persona__apellido1'] = ''
        if 'cod_persona__apellido2' not in inv:
            inv['cod_persona__apellido2'] = ''
        if 'cod_cce__descripcion' not in inv:
            inv['cod_cce_descripcion'] = ''
        return inv


class WSDeptReport(WSReport):
    report_type = st_cvn.REPORTS_DIRECTORY.DEPT.value
    WS_URL_ALL = st.WS_DEPARTMENTS_ALL
    WS_URL_DETAIL = st.WS_DEPARTMENTS_AND_MEMBERS_UNIT_YEAR


class WSAreaReport(WSReport):
    report_type = st_cvn.REPORTS_DIRECTORY.AREA.value
    WS_URL_ALL = st.WS_AREAS_ALL
    WS_URL_DETAIL = st.WS_AREAS_AND_MEMBERS_UNIT_YEAR