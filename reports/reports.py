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
from django.conf import settings as st
from core.routers import in_database
from cvn import settings as st_cvn
from cvn.models import (Articulo, Libro, Capitulo, Congreso, Proyecto,
                        Convenio, TesisDoctoral, Patente, ReportDept,
                        ReportArea)
from core.models import UserProfile

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
        with in_database(st.HISTORICAL[str(self.year)]):
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


class UnitReport(BaseReport):
    Report = None

    def get_all_units(self):
        with in_database(st.HISTORICAL[str(self.year)]):
            return list(self.Report.objects.exclude(reportmember=None).order_by(
                'name'))

    def get_investigadores(self, unit, title):
        with in_database(st.HISTORICAL[str(self.year)]):
            if unit is None:
                return NotImplemented
            members = unit.reportmember_set.all().order_by(
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
                title = unit.name
            return investigadores, usuarios, title

    @classmethod
    def get_unit_name(cls, code, year):
        with in_database(st.HISTORICAL[str(year)]):
            return cls.Report.objects.get(code=code).name

    @classmethod
    def get_all_units_names(cls, year):
        with in_database(st.HISTORICAL[str(year)]):
            return list(cls.Report.objects.all())


class DeptReport(UnitReport):
    report_type = st_cvn.REPORTS_DIRECTORY.DEPT.value
    Report = ReportDept


class AreaReport(UnitReport):
    report_type = st_cvn.REPORTS_DIRECTORY.AREA.value
    Report = ReportArea
