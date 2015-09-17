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
        articulos = Articulo.objects.byUsuariosYear(profiles, self.year)
        libros = Libro.objects.byUsuariosYear(profiles, self.year)
        capitulos_libro = Capitulo.objects.byUsuariosYear(profiles, self.year)
        congresos = Congreso.objects.byUsuariosYear(profiles, self.year)
        proyectos = Proyecto.objects.byUsuariosYear(profiles, self.year)
        convenios = Convenio.objects.byUsuariosYear(profiles, self.year)
        tesis = TesisDoctoral.objects.byUsuariosYear(profiles, self.year)
        patentes = Patente.objects.byUsuariosYear(profiles, self.year)
        self.generator.go(unit_name, inv, articulos, libros, capitulos_libro,
                          congresos, proyectos, convenios, tesis, patentes)


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
                logger.warn(u"No se encuentran "
                            u"los siguientes "
                            u"usuarios: " + str(nonexistent_users))
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
        return self.Report.objects.all()

    def get_investigadores(self, unit, title):
        if unit is None:
            return NotImplemented

        members = unit.reportmember_set.all()
        if not members:
            logger.warn((
                u"La unidad " + unicode(unit.name) + u" no tiene "
                                                     u"información en " +
                unicode(self.year)))
            return [], [], unit.name

        investigadores = []
        usuarios = []
        for member in members:
            usuarios.append(member.user_profile)
            investigador = {
                'cod_persona__nombre': member.user_profile.user.first_name,
                'cod_persona__apellido1': member.user_profile.user.last_name,
                'cod_persona__apellido2': '',
                'cod_cce__descripcion': member.cce
            }
            investigadores.append(investigador)

        if title is None:
            title = unit.name
        return investigadores, usuarios, title


class DeptReport(UnitReport):
    report_type = st_cvn.REPORTS_DIRECTORY.DEPT.value
    Report = ReportDept


class AreaReport(UnitReport):
    report_type = st_cvn.REPORTS_DIRECTORY.AREA.value
    Report = ReportArea
