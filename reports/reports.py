# -*- encoding: UTF-8 -*-

from abc import ABCMeta
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings as st
from cvn.models import (Articulo, Libro, Capitulo, Congreso, Proyecto,
                        Convenio, TesisDoctoral, Patente)
from statistics.models import Area, Department
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
        try:
            inv, profiles, unit_name = self.get_investigadores(unit, title)
        except UnitDoesNotExist:
            print('ERROR: La unidad ' + unit + ' no existe\n')
            return
        articulos = Articulo.objects.byUsuariosYear(profiles, self.year)
        libros = Libro.objects.byUsuariosYear(profiles, self.year)
        capitulos_libro = Capitulo.objects.byUsuariosYear(profiles, self.year)
        congresos = Congreso.objects.byUsuariosYear(profiles, self.year)
        proyectos = Proyecto.objects.byUsuariosYear(profiles, self.year)
        convenios = Convenio.objects.byUsuariosYear(profiles, self.year)
        tesis = TesisDoctoral.objects.byUsuariosYear(profiles, self.year)
        patentes = Patente.objects.byUsuariosYear(profiles, self.year)
        print('Generando Informe para ' + unit_name + "...\n")
        if inv:
            self.generator.go(unit_name, inv,articulos, libros, capitulos_libro,
                              congresos, proyectos, convenios, tesis, patentes)
            print('OK\n')
        else:
            print('ERROR: No hay Investigadores\n')


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

    Unit = None
    WS_URL = None

    def get_all_units(self):
        return self.Unit.objects.values_list('code', flat=True)

    def get_investigadores(self, unit, title):
        unit_content = ws.get(self.WS_URL % (unit, self.year))[0]
        if unit_content["unidad"] == {}:
            raise UnitDoesNotExist
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
    Unit = Department
    WS_URL = st.WS_DEPARTMENTS_AND_MEMBERS_UNIT_YEAR


class AreaReport(UnitReport):
    report_type = 'area'
    Unit = Area
    WS_URL = st.WS_AREAS_AND_MEMBERS_UNIT_YEAR


class UnitDoesNotExist(Exception):
    pass