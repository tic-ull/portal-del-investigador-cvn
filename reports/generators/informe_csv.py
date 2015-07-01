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
from django.conf import settings as st


def write_producciones(csv_writer, name, producciones, fields):
    csv_writer.writerow([])
    csv_writer.writerow([name])
    csv_writer.writerow(fields)
    for produccion in producciones:
        row = [getattr(produccion, field) for field in fields]
        csv_writer.writerow(row)


class InformeCSV:
    # Do not touch the method definitions if you don't know what you are doing.
    # (All the generators should have the same definitions)

    def __init__(self, year, model_type):
        self.year = str(year)
        self.model_type = model_type

    @staticmethod
    def get_save_path(year, model_type):
        return "%s/%s/%s/" % (st_cvn.REPORTS_ICSV_ROOT, model_type, year)

    def go(self, team_name, investigadores, articulos, libros, capitulos,
           congresos, proyectos, convenios, tesis, patentes):
        path = self.get_save_path(self.year, self.model_type)
        if not os.path.isdir(path):
            os.makedirs(path)
        file_name = slugify(self.year + "-" + team_name) + ".csv"
        file_path = os.path.join(path, file_name)
        with open(file_path, 'wb') as csvfile:
            csv_writer = csv.writer(csvfile, dialect=st.CSV_DIALECT)
            write_producciones(csv_writer, u'Artículos', articulos,
                               st_cvn.INFORME_CSV_FIELDS_ARTICULO)
            write_producciones(csv_writer, u'Libros', libros,
                               st_cvn.INFORME_CSV_FIELDS_LIBRO)
            write_producciones(csv_writer, u'Capítulos', capitulos,
                               st_cvn.INFORME_CSV_FIELDS_CAPITULO)
            write_producciones(csv_writer, u'Congresos', congresos,
                               st_cvn.INFORME_CSV_FIELDS_CONGRESO)
            write_producciones(csv_writer, u'Proyecto', proyectos,
                               st_cvn.INFORME_CSV_FIELDS_PROYECTO)
            write_producciones(csv_writer, u'Convenios', convenios,
                               st_cvn.INFORME_CSV_FIELDS_CONVENIO)
            write_producciones(csv_writer, u'Tesis Doctorales', tesis,
                               st_cvn.INFORME_CSV_FIELDS_TESIS)
            write_producciones(csv_writer, u'Patentes', patentes,
                               st_cvn.INFORME_CSV_FIELDS_PATENTE)
        return file_path