# -*- encoding: UTF-8 -*-

from abc import ABCMeta
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings as st
from cvn.models import (Articulo, Libro, Capitulo, Congreso, Proyecto,
                        Convenio, TesisDoctoral, Patente)
from core.models import UserProfile
from core.ws_utils import CachedWS as ws


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

    def create_report(self, unit, title=None):
        inv, profiles, unit_name = self.get_investigadores(unit, title)
        if not inv:
            print(u'WARNING: No hay Investigadores en la unidad ' + unit_name
                  + u' en el año ' + unicode(self.year)
                  + u'. No se generará informe\n')
            return
        articulos = Articulo.objects.byUsuariosYear(profiles, self.year)
        libros = Libro.objects.byUsuariosYear(profiles, self.year)
        capitulos_libro = Capitulo.objects.byUsuariosYear(profiles, self.year)
        congresos = Congreso.objects.byUsuariosYear(profiles, self.year)
        proyectos = Proyecto.objects.byUsuariosYear(profiles, self.year)
        convenios = Convenio.objects.byUsuariosYear(profiles, self.year)
        tesis = TesisDoctoral.objects.byUsuariosYear(profiles, self.year)
        patentes = Patente.objects.byUsuariosYear(profiles, self.year)
        print(u'Generando Informe para ' + unit_name + u"...\n")
        self.generator.go(unit_name, inv,articulos, libros, capitulos_libro,
                          congresos, proyectos, convenios, tesis, patentes)


class ListReport(BaseReport):

    report_type = 'list'

    def get_investigadores(self, unit, title):
        profiles = UserProfile.objects.filter(documento__in=unit)
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

    def get_all_units(self):
        units = ws.get(self.WS_URL_ALL)
        # Save unit names bc the ws doesn't return it when there are no members
        self.unit_names = {}
        for unit in units:
            self.unit_names[unit['codigo']] = unit['nombre']
        return map(lambda x: x['codigo'], units)

    def get_investigadores(self, unit, title):
        unit_content = ws.get(self.WS_URL_DETAIL % (unit, self.year))[0]
        if unit_content["unidad"] == {}:
            return [], [], self.unit_names[unit]
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
    report_type = 'department'
    WS_URL_ALL = st.WS_DEPARTMENTS_ALL
    WS_URL_DETAIL = st.WS_DEPARTMENTS_AND_MEMBERS_UNIT_YEAR


class AreaReport(UnitReport):
    report_type = 'area'
    WS_URL_ALL = st.WS_AREAS_ALL
    WS_URL_DETAIL = st.WS_AREAS_AND_MEMBERS_UNIT_YEAR