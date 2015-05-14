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

    def __init__(self, year, model_type):
        self.year = str(year)
        self.header = [u'Nombre', u'Investigadores', u'Artículos', u'Libros',
                       u'Capítulos', u'Congresos', u'Proyectos', u'Convenios',
                       u'Tesis', u'Propiedad Intelectual']
        path = "%s/%s/%s/" % (st_cvn.REPORTS_CSV_ROOT, model_type,
                              self.year)
        if not os.path.isdir(path):
            os.makedirs(path)
        self.filename = os.path.join(path, self.year +
                                     '-' + model_type + ".csv")
        self.writer = csv.DictWriter(open(self.filename, 'wb'),
                                dialect=st.CSV_DIALECT,
                                fieldnames=self.header)
        self.writer.writeheader()

    def go(self, team_name, investigadores, articulos, libros, capitulos,
           congresos, proyectos, convenios, tesis, patentes):
        self.team_name = team_name
        self.investigadores = len(investigadores)
        self.articulos = len(articulos)
        self.libros = len(libros)
        self.capitulos = len(capitulos)
        self.congresos = len(congresos)
        self.proyectos = len(proyectos)
        self.convenios = len(convenios)
        self.tesis = len(tesis)
        self.patentes = len(patentes)
        self.writer.writerow({u'Nombre': self.team_name,
                              u'Investigadores': self.investigadores,
                              u'Artículos': self.articulos,
                              u'Libros': self.libros,
                              u'Capítulos': self.capitulos,
                              u'Congresos': self.congresos,
                              u'Proyectos': self.proyectos,
                              u'Convenios': self.convenios,
                              u'Tesis': self.tesis,
                              u'Propiedad Intelectual': self.patentes})
