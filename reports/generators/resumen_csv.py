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
        full_path = os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_RCSV_PATH)
        path = "%s/%s/%s/" % (full_path, model_type,
                              self.year)
        if not os.path.isdir(path):
            os.makedirs(path)
        self.filename = os.path.join(path, self.year +
                                     '-' + model_type + ".csv")
        self._file = open(self.filename, 'wb')
        self.writer = csv.DictWriter(self._file, dialect=st.CSV_DIALECT,
            fieldnames=[u'Nombre', u'Investigadores', u'Artículos', u'Libros',
                        u'Capítulos', u'Congresos', u'Proyectos', u'Convenios',
                        u'Tesis', u'Propiedad Intelectual']
        )
        self.writer.writeheader()

    def go(self, team_name, investigadores, articulos, libros, capitulos,
           congresos, proyectos, convenios, tesis, patentes):
        self.writer.writerow({u'Nombre': team_name,
                              u'Investigadores': len(investigadores),
                              u'Artículos': len(articulos),
                              u'Libros': len(libros),
                              u'Capítulos': len(capitulos),
                              u'Congresos': len(congresos),
                              u'Proyectos': len(proyectos),
                              u'Convenios': len(convenios),
                              u'Tesis': len(tesis),
                              u'Propiedad Intelectual': len(patentes)})