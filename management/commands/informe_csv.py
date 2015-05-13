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

import unicodecsv as csv
import os
from slugify import slugify
from cvn import settings as st_cvn


def write_producciones(csv_writer, name, producciones, fields):
    csv_writer.writerow([])
    csv_writer.writerow([name])
    csv_writer.writerow(fields)
    for produccion in producciones:
        row = [getattr(produccion, field) for field in fields]
        csv_writer.writerow(row)


class InformeCSV:

    def __init__(self, year, unidad, investigadores, articulos, libros,
                 capitulos_libro, congresos, proyectos, convenios, tesis,
                 patentes, model_type):
        self.year = str(year)
        self.unidad = unidad
        self.articulos = articulos
        self.libros = libros
        self.capitulosLibro = capitulos_libro
        self.congresos = congresos
        self.proyectos = proyectos
        self.convenios = convenios
        self.tesis = tesis
        self.patentes = patentes
        self.model_type = model_type

    def go(self):
        path = "%s/%s/%s/" % (st_cvn.REPORTS_ICSV_ROOT, self.model_type,
                              self.year)
        if not os.path.isdir(path):
            os.makedirs(path)
        file_name = slugify(self.year + "-" + self.unidad) + ".csv"
        file_path = os.path.join(path, file_name)
        with open(file_path, 'wb') as csvfile:
            csv_writer = csv.writer(csvfile, dialect="investigacion")
            write_producciones(csv_writer, u'Artículos', self.articulos,
                               st_cvn.INFORME_CSV_FIELDS_ARTICULO)
            write_producciones(csv_writer, u'Libros', self.libros,
                               st_cvn.INFORME_CSV_FIELDS_LIBRO)
            write_producciones(csv_writer, u'Capítulos', self.capitulosLibro,
                               st_cvn.INFORME_CSV_FIELDS_CAPITULO)
            write_producciones(csv_writer, u'Congresos', self.congresos,
                               st_cvn.INFORME_CSV_FIELDS_CONGRESO)
            write_producciones(csv_writer, u'Proyecto', self.proyectos,
                               st_cvn.INFORME_CSV_FIELDS_PROYECTO)
            write_producciones(csv_writer, u'Convenios', self.convenios,
                               st_cvn.INFORME_CSV_FIELDS_CONVENIO)
            write_producciones(csv_writer, u'Tesis Doctorales', self.tesis,
                               st_cvn.INFORME_CSV_FIELDS_TESIS)
            write_producciones(csv_writer, u'Patentes', self.patentes,
                               st_cvn.INFORME_CSV_FIELDS_PATENTE)