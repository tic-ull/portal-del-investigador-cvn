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

from cvn import settings as st_cvn
import os
import unicodecsv as csv
from django.conf import settings as st


class ResumenCSV:

    def __init__(self, year, departamento, investigadores, articulos, libros,
                 capitulos_libro, congresos, proyectos, convenios, tesis,
                 patentes, model_type):
        self.year = str(year)
        self.departamento = departamento.encode('utf-8')
        self.investigadores = len(investigadores)
        self.articulos = len(articulos)
        self.libros = len(libros)
        self.capitulos = len(capitulos_libro)
        self.congresos = len(congresos)
        self.proyectos = len(proyectos)
        self.convenios = len(convenios)
        self.tesis = len(tesis)
        self.patentes = len(patentes)
        self.model_type = model_type
        self.header = [u'Nombre', u'Investigadores', u'Artículos', u'Libros',
                       u'Capítulos', u'Congresos', u'Proyectos', u'Convenios',
                       u'Tesis', u'Propiedad Intelectual']
        path = "%s/%s/%s/" % (st_cvn.REPORTS_CSV_ROOT, self.model_type,
                              self.year)
        if not os.path.isdir(path):
            os.makedirs(path)
        self.filename = os.path.join(path, self.year +
                                     '-' + model_type + ".csv")

    def go(self):
        isfile = os.path.isfile(self.filename)
        writer = csv.DictWriter(open(self.filename, 'awb'),
                                dialect=st.CSV_DIALECT,
                                fieldnames=self.header)
        if not isfile:
            writer.writeheader()
        writer.writerow({u'Nombre': self.departamento,
                         u'Investigadores': self.investigadores,
                         u'Artículos': self.articulos,
                         u'Libros': self.libros,
                         u'Capítulos': self.capitulos,
                         u'Congresos': self.congresos,
                         u'Proyectos': self.proyectos,
                         u'Convenios': self.convenios,
                         u'Tesis': self.tesis,
                         u'Propiedad Intelectual': self.patentes})
