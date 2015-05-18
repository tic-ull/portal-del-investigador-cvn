# -*- encoding: UTF-8 -*-

from abc import ABCMeta
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings as st
from cvn.models import (Articulo, Libro, Capitulo, Congreso, Proyecto,
                        Convenio, TesisDoctoral, Patente)
from statistics.models import Area, Department
from core.models import UserProfile
from core.ws_utils import CachedWS as ws


class Report:

    __metaclass__ = ABCMeta

    def __init__(self, generator):
        self.generator = generator

    def get_all_units(self):
        # Override this if you want to call create_reports with empty units
        return []

    def get_investigadores(self, unit, year, title):
        return NotImplemented

    def create_reports(self, year, units=None):
        if units is None:
            units = self.get_all_units()
        for unit in units:
            self.create_report(year, unit)

    def create_report(self, year, unit, title=None):
        inv, profiles, unit_name = self.get_investigadores(unit, year, title)
        articulos = Articulo.objects.byUsuariosYear(profiles, year)
        libros = Libro.objects.byUsuariosYear(profiles, year)
        capitulos_libro = Capitulo.objects.byUsuariosYear(profiles, year)
        congresos = Congreso.objects.byUsuariosYear(profiles, year)
        proyectos = Proyecto.objects.byUsuariosYear(profiles, year)
        convenios = Convenio.objects.byUsuariosYear(profiles, year)
        tesis = TesisDoctoral.objects.byUsuariosYear(profiles, year)
        patentes = Patente.objects.byUsuariosYear(profiles, year)
        print('Generando Informe para ' + unit_name + "...\n")
        if inv:
            self.generator.go(unit_name, inv,articulos, libros, capitulos_libro,
                              congresos, proyectos, convenios, tesis, patentes)
            print('OK\n')
        else:
            print('ERROR: No hay Investigadores\n')


class ListReport(Report):

    def get_investigadores(self, unit, year, title):
        profiles = UserProfile.objects.filter(documento__in=unit)
        investigadores = [{'cod_persona__nombre': p.user.first_name,
                           'cod_persona__apellido1': p.user.last_name,
                           'cod_persona__apellido2': '',
                           'cod_cce__descripcion': ''}
                          for p in profiles]
        if title is None:
            title = ';'.join(unit)
        return investigadores, profiles, title


class UnitReport(Report):

    Unit = None
    WS_URL = None

    def get_all_units(self):
        return self.Unit.objects.values_list('code', flat=True)

    def get_investigadores(self, unit, year, title):
        unit_content = ws.get(self.WS_URL % (unit, year))[0]
        investigadores = list()
        usuarios = list()
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
    Unit = Department
    WS_URL = st.WS_DEPARTMENTS_AND_MEMBERS_UNIT_YEAR


class AreaReport(UnitReport):
    Unit = Area
    WS_URL = st.WS_AREAS_AND_MEMBERS_UNIT_YEAR