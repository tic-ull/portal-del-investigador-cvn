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

from core.models import UserProfile
from core.ws_utils import CachedWS as ws
from cvn.models import (Articulo, Libro, Capitulo, Congreso, Proyecto,
                        Convenio, TesisDoctoral, Patente)
from cvn.utils import isdigit
from django.conf import settings as st
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from resumen_csv import ResumenCSV
from informe_pdf import InformePDF
from informe_csv import InformeCSV
from optparse import make_option


class Command(BaseCommand):
    help = u'Genera un PDF/CSV con los datos de una lista de usuarios'
    option_list = BaseCommand.option_list + (
        make_option(
            "-l",
            "--list",
            dest="list",
            default="",
            help="List of NIFs from the users of the report",
        ),
        make_option(
            "-f",
            "--format",
            dest="format",
            default='pdf',
            help="Specify the output format",
        ),
        make_option(
            "-t",
            "--title",
            dest="title",
            default=u'Producción científica',
            help="Specify a name for the list of users",
        ),
        make_option(
            "-y",
            "--year",
            dest="year",
            help="Specify the year in format YYYY",
        ),
    )

    def handle(self, *args, **options):
        self.check_args(options)
        if options['format'] == 'pdf':
            self.generator = InformePDF
        elif options['format'] == 'icsv':
            self.generator = InformeCSV
        else:
            self.generator = ResumenCSV
        nifs = options["list"].split(",")
        self.create_report(int(options['year']), nifs, options['title'])

    def check_args(self, options):
        f = options['format']
        if not f == 'pdf' and not f == 'csv' and not f == 'icsv':
            raise CommandError("Option `--format=X` must be pdf, csv or icsv")
        if not isdigit(options['year']):
            raise CommandError(
                "Option `--year=YYYY` must exist and be a number")

    def create_report(self, year, nifs, title):
        (investigadores, articulos,
         libros, capitulos_libro, congresos, proyectos,
         convenios, tesis, patentes) = self.get_data(year, nifs)
        if investigadores:
            informe = self.generator(year, title, investigadores,
                                     articulos, libros, capitulos_libro,
                                     congresos, proyectos, convenios, tesis,
                                     patentes, 'list')
            informe.go()
            print 'OK\n'
        else:
            print 'ERROR: No hay Investigadores\n'

    def get_data(self, year, nifs):
        investigadores, usuarios = self.get_investigadores(nifs)
        articulos = Articulo.objects.byUsuariosYear(usuarios, year)
        libros = Libro.objects.byUsuariosYear(usuarios, year)
        capitulos_libro = Capitulo.objects.byUsuariosYear(usuarios, year)
        congresos = Congreso.objects.byUsuariosYear(usuarios, year)
        proyectos = Proyecto.objects.byUsuariosYear(usuarios, year)
        convenios = Convenio.objects.byUsuariosYear(usuarios, year)
        tesis = TesisDoctoral.objects.byUsuariosYear(usuarios, year)
        patentes = Patente.objects.byUsuariosYear(usuarios, year)
        return (investigadores, articulos,
                libros, capitulos_libro, congresos, proyectos,
                convenios, tesis, patentes)

    def get_investigadores(self, nifs):
        profiles = UserProfile.objects.filter(documento__in=nifs)
        investigadores = [{'cod_persona__nombre': p.user.first_name,
                           'cod_persona__apellido1': p.user.last_name,
                           'cod_persona__apellido2': '',
                           'cod_cce__descripcion': ''}
                          for p in profiles]
        return investigadores, profiles