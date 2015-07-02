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

from PIL import Image
from xml.sax.saxutils import escape
from cvn import settings as st_cvn
from django.utils import translation
from django.utils.translation import ugettext
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle)
from reportlab.platypus.flowables import PageBreak
from slugify import slugify
import os


class InformePDF:
    # Do not touch the method definitions if you don't know what you are doing.
    # (All the generators should have the same definitions)

    BLUE_SECONDARY_ULL = colors.HexColor('#EBF3FA')
    BLUE_ULL = colors.HexColor('#006699')
    DEFAULT_FONT = 'Helvetica'
    DEFAULT_FONT_BOLD = 'Helvetica-Bold'
    DEFAULT_SPACER = 0.1 * inch
    HEADER_FONT_SIZE = 14
    MARGIN = 10 * mm
    PAGE_HEIGHT = A4[1]
    PAGE_NUMBERS_MARGIN = 0.75 * MARGIN
    PAGE_NUMBERS_SIZE = 8
    PAGE_WIDTH = A4[0]
    VIOLET_ULL = colors.HexColor('#7A3B7A')

    def __init__(self, year, model_type):
        self.year = str(year)
        self.model_type = model_type
        self.set_logo()

    @staticmethod
    def get_save_path(year, model_type):
        return "%s/%s/%s/" % (st_cvn.REPORTS_IPDF_ROOT, model_type, year)

    @staticmethod
    def get_filename(year, team_name, model_type=None):
        return slugify(str(year) + "-" + team_name) + ".pdf"

    def go(self, team_name, investigadores, articulos, libros, capitulos,
           congresos, proyectos, convenios, tesis, patentes):
        self.team_name = team_name
        path_file = self.get_save_path(self.year, self.model_type)
        if not os.path.isdir(path_file):
            os.makedirs(path_file)
        file_name = self.get_filename(self.year, team_name)
        full_path = path_file + file_name
        doc = SimpleDocTemplate(full_path)
        story = [Spacer(1, 3 * self.DEFAULT_SPACER)]
        self.show_investigadores(story, investigadores)
        self.show_articulos(story, articulos)
        self.show_libros(story, libros)
        self.show_capitulos(story, capitulos)
        self.show_congresos(story, congresos)
        self.show_proyectos(story, proyectos)
        self.show_convenios(story, convenios)
        self.show_tesis(story, tesis)
        self.show_patentes(story, patentes)
        doc.build(story, onFirstPage=self.first_page,
                  onLaterPages=self.later_pages)
        return full_path

    def set_logo(self):
        img_path = st_cvn.REPORTS_IMAGES
        if not os.path.exists(img_path + 'logo' + self.year + '.png'):
            logo = 'logo.png'
        else:
            logo = 'logo' + self.year + '.png'
        self.logo_path = img_path + logo

        self.logo_width, self.logo_height = Image.open(self.logo_path).size

        logo_scale = 0.35
        self.logo_width *= logo_scale
        self.logo_height *= logo_scale

    # -------------------------------------------------------------------------
    # PROCESADO DE LOS DATOS
    # -------------------------------------------------------------------------

    def show_investigadores(self, story, investigadores):
        if not investigadores:
            return
        story.append(Paragraph('INVESTIGADORES', self.style_h3()))
        text = 'Número de investigadores: ' + str(len(investigadores))
        story.append(Paragraph(text, self.style_n()))
        story.append(Spacer(1, 1 * self.DEFAULT_SPACER))
        story.append(self.table_investigadores(investigadores))

    def table_investigadores(self, investigadores):
        table_inv = []
        for inv in investigadores:
            table_inv.append([
                inv['cod_persona__nombre'],
                (inv['cod_persona__apellido1'] + ' ' +
                 inv['cod_persona__apellido2']),
                inv['cod_cce__descripcion']])
        HEADERS = ["NOMBRE", "APELLIDOS", "CATEGORÍA"]
        data = [HEADERS] + table_inv
        table = Table(data, repeatRows=1)
        table.setStyle(self.style_table())
        return table

    # -------------------------------------------------------------------------

    def show_articulos(self, story, articulos):
        if not articulos:
            return
        story.append(PageBreak())
        story.append(Paragraph('ARTÍCULOS', self.style_h3()))
        text = 'Número de artículos: ' + str(len(articulos))
        story.append(Paragraph(text, self.style_n()))
        self.list_articulos(story, articulos)

    def list_articulos(self, story, articulos):
        for art in articulos:
            text = ""
            if art.fecha:
                text += u"<b>Fecha:</b> %s <br/>" % (
                    art.fecha.strftime("%d/%m/%Y")
                )
            if art.titulo:
                text += u"<b>%s</b><br/>" % escape(art.titulo)
            if art.autores:
                text += u"%s<br/>" % art.autores
            if art.nombre_publicacion:
                text += u"%s<br/>" % art.nombre_publicacion
            if art.volumen:
                text += u"Vol. %s &nbsp; &nbsp;" % art.volumen
            if art.numero:
                text += u"Núm. %s &nbsp; &nbsp;" % art.numero
            if art.pagina_inicial and art.pagina_final:
                text += u"Pág. %s-%s &nbsp; &nbsp;" % (
                    art.pagina_inicial,
                    art.pagina_final
                )
            if art.issn:
                text += u"ISSN: %s" % art.issn
            story.append(Paragraph(text, self.style_n()))

    # -------------------------------------------------------------------------

    def show_libros(self, story, libros):
        if not libros:
            return
        story.append(PageBreak())
        story.append(Paragraph('LIBROS', self.style_h3()))
        text = 'Número de libros: ' + str(len(libros))
        story.append(Paragraph(text, self.style_n()))
        self.list_libros(story, libros)

    def list_libros(self, story, libros):
        for libro in libros:
            text = ""
            if libro.fecha:
                text += u"<b>Fecha:</b> %s <br/>" % (
                    libro.fecha.strftime("%d/%m/%Y")
                )
            if libro.titulo:
                text += u"<b>%s</b><br/>" % libro.titulo
            if libro.autores:
                text += u"%s<br/>" % libro.autores
            if libro.nombre_publicacion:
                text += u"%s<br/>" % libro.nombre_publicacion
            if libro.isbn:
                text += u"ISBN: %s" % libro.isbn
            story.append(Paragraph(text, self.style_n()))

    # -------------------------------------------------------------------------

    def show_capitulos(self, story, capitulos):
        if not capitulos:
            return
        story.append(PageBreak())
        story.append(Paragraph('CAPÍTULOS DE LIBROS', self.style_h3()))
        text = 'Número de capítulos de libros: ' + str(len(capitulos))
        story.append(Paragraph(text, self.style_n()))
        self.list_capitulos(story, capitulos)

    def list_capitulos(self, story, capitulos):
        for capLibro in capitulos:
            text = ""
            if capLibro.fecha:
                text += u"<b>Fecha:</b> %s <br/>" % (
                    capLibro.fecha.strftime("%d/%m/%Y")
                )
            if capLibro.titulo:
                text += u"<b>%s</b><br/>" % capLibro.titulo
            if capLibro.autores:
                text += u"%s<br/>" % capLibro.autores
            if capLibro.nombre_publicacion:
                text += u"%s &nbsp; &nbsp;" % capLibro.nombre_publicacion
            if capLibro.pagina_inicial and capLibro.pagina_final:
                text += u"Pág. %s-%s &nbsp; &nbsp;" % (
                    capLibro.pagina_inicial,
                    capLibro.pagina_final
                )
            if capLibro.isbn:
                text += u"ISBN: %s" % capLibro.isbn
            story.append(Paragraph(text, self.style_n()))

    # -------------------------------------------------------------------------

    def show_congresos(self, story, congresos):
        if not congresos:
            return
        story.append(PageBreak())
        story.append(Paragraph('COMUNICACIONES EN CONGRESOS', self.style_h3()))
        text = 'Número de comunicaciones en congresos: ' + str(len(congresos))
        story.append(Paragraph(text, self.style_n()))
        self.list_congresos(story, congresos)

    def list_congresos(self, story, congresos):
        translation.activate('es')
        for congreso in congresos:
            text = ""
            if congreso.titulo:
                text += u"<b>%s</b><br/>" % congreso.titulo
            if congreso.nombre_del_congreso:
                text += u"%s " % congreso.nombre_del_congreso
            if congreso.ciudad_de_realizacion and congreso.fecha_de_inicio:
                translation.activate('es')
                text += "(%s, %s de %s)<br/>" % (
                    congreso.ciudad_de_realizacion,
                    ugettext(congreso.fecha_de_inicio.strftime("%B")),
                    congreso.fecha_de_inicio.strftime("%Y")
                )
            elif congreso.ciudad_de_realizacion:
                text += "(%s)<br/>" % congreso.ciudad_de_realizacion
            elif congreso.fecha_de_inicio:
                text += "(%s)<br/>" % congreso.fecha_de_inicio
            if congreso.autores:
                text += u"%s" % congreso.autores
            story.append(Paragraph(text, self.style_n()))
        translation.deactivate()

    # -------------------------------------------------------------------------

    def show_proyectos(self, story, proyectos):
        if not proyectos:
            return
        story.append(PageBreak())
        story.append(Paragraph('PROYECTOS ACTIVOS', self.style_h3()))
        text = 'Número de proyectos activos: ' + str(len(proyectos))
        story.append(Paragraph(text, self.style_n()))
        self.list_proyectos(story, proyectos)

    def list_proyectos(self, story, proyectos):
        for proy in proyectos:
            text = ""
            if proy.titulo:
                text += u"<b>%s</b><br/>" % proy.titulo
            if proy.fecha_de_inicio:
                text += u"Fecha de inicio: %s<br/>" % (
                    proy.fecha_de_inicio.strftime("%d/%m/%Y")
                )
            if proy.fecha_de_fin:
                text += u"Fecha de finalización: %s<br/>" % (
                    proy.fecha_de_fin.strftime("%d/%m/%Y")
                )
            if proy.cuantia_total:
                text += u"Cuantía: %s<br/>" % proy.cuantia_total
            if proy.autores:
                text += u"Investigadores: %s" % proy.autores
            story.append(Paragraph(text, self.style_n()))

    # -------------------------------------------------------------------------

    def show_convenios(self, story, convenios):
        if not convenios:
            return
        story.append(PageBreak())
        story.append(Paragraph('CONVENIOS ACTIVOS', self.style_h3()))
        text = 'Número de convenios activos: ' + str(len(convenios))
        story.append(Paragraph(text, self.style_n()))
        self.list_convenios(story, convenios)

    def list_convenios(self, story, convenios):
        for conv in convenios:
            text = ""
            if conv.titulo:
                text += u"<b>%s</b><br/>" % conv.titulo
            if conv.fecha_de_inicio:
                text += u"Fecha de inicio: %s<br/>" % (
                    conv.fecha_de_inicio.strftime("%d/%m/%Y")
                )
            if conv.fecha_de_fin is not None:
                text += u"Fecha de finalización: %s<br/>" % (
                    conv.fecha_de_fin.strftime("%d/%m/%Y")
                )
            if conv.cuantia_total:
                text += u"Cuantía: %s<br/>" % conv.cuantia_total
            if conv.autores:
                text += u"Investigadores: %s" % conv.autores
            story.append(Paragraph(text, self.style_n()))

    # -------------------------------------------------------------------------

    def show_tesis(self, story, tesis):
        if not tesis:
            return
        story.append(PageBreak())
        story.append(Paragraph('TESIS DOCTORALES', self.style_h3()))
        text = 'Número de tesis doctorales: ' + str(len(tesis))
        story.append(Paragraph(text, self.style_n()))
        self.list_tesis(story, tesis)

    def list_tesis(self, story, tesis):
        for t in tesis:
            text = ""
            if t.titulo:
                text += u"<b>%s</b><br/>" % t.titulo
            if t.autor:
                text += u"Doctorando: %s<br/>" % t.autor
            if t.universidad_que_titula:
                text += u"Universidad: %s<br/>" % (
                    t.universidad_que_titula
                )
            if t.user_profile:
                text += u"Director: %s" % u",".join(
                    [u.user.first_name + u" " + u.user.last_name
                     for u in t.user_profile.all()])
                text += u"<br/>"
            if t.codirector:
                text += u"Codirector: %s" % t.codirector
            if t.fecha:
                text += u"Fecha de lectura: %s<br/>" % (
                    t.fecha.strftime("%d/%m/%Y")
                )
            story.append(Paragraph(text, self.style_n()))

    # -------------------------------------------------------------------------

    def show_patentes(self, story, patentes):
        if not patentes:
            return
        story.append(PageBreak())
        story.append(Paragraph('PROPIEDAD INTELECTUAL', self.style_h3()))
        text = 'Número de Propiedades Intelectuales: ' + str(len(patentes))
        story.append(Paragraph(text, self.style_n()))
        self.list_patentes(story, patentes)

    def list_patentes(self, story, patentes):
        for pat in patentes:
            text = ""
            if pat.titulo:
                text += u"<b>%s</b><br/>" % pat.titulo
            if pat.num_solicitud:
                text += u"Número de solicitud: %s <br/>" % pat.num_solicitud
            if pat.fecha:
                text += u"Fecha de registro: %s <br/>" % (
                    pat.fecha.strftime("%d/%m/%Y")
                )
            if pat.fecha_concesion:
                text += u"Fecha de concesión: %s <br/>" % (
                    pat.fecha_concesion.strftime("%d/%m/%Y")
                )
            if pat.lugar_prioritario:
                text += u"Inscrita en: "
                if pat.lugar_prioritario:
                    text += pat.lugar_prioritario
                text += u"<br/>"
            if pat.autores:
                text += u"%s<br/>" % pat.autores
            if pat.entidad_titular:
                text += u"%s<br/>" % pat.entidad_titular
            story.append(Paragraph(text, self.style_n()))

    # -------------------------------------------------------------------------
    # CONFIGURACIÓN DE LAS PÁGINAS
    # -------------------------------------------------------------------------

    def first_page(self, canvas, doc):
        canvas.saveState()
        self.header(canvas)
        canvas.restoreState()

    def later_pages(self, canvas, doc):
        canvas.saveState()
        self.header(canvas)
        canvas.setFont(self.DEFAULT_FONT, self.PAGE_NUMBERS_SIZE)
        canvas.drawCentredString(self.PAGE_WIDTH / 2.0,
                                 self.PAGE_NUMBERS_MARGIN,
                                 u'Página %s - %s' % (doc.page, self.team_name))
        canvas.restoreState()

    def header(self, canvas):
        canvas.setFont(self.DEFAULT_FONT_BOLD, self.HEADER_FONT_SIZE)
        canvas.setFillColor(self.BLUE_ULL)
        canvas.drawString(self.MARGIN, self.PAGE_HEIGHT - 2 * self.MARGIN,
                          self.team_name)
        canvas.drawImage(self.logo_path,
                         self.PAGE_WIDTH - self.MARGIN - self.logo_width,
                         self.PAGE_HEIGHT - self.logo_height - self.MARGIN,
                         self.logo_width,
                         self.logo_height)

    # --------------------------------------------------------------------
    # ESTILOS DEL PDF
    # --------------------------------------------------------------------

    def style_n(self):
        style = getSampleStyleSheet()['Normal']
        style.leading = 12
        style.allowWidows = 0
        style.spaceBefore = 0.2 * inch
        return style

    def style_h3(self):
        style = getSampleStyleSheet()['Heading3']
        style.textColor = self.VIOLET_ULL
        return style

    def style_table(self):
        style = TableStyle(
            [('SIZE', (0, 0), (-1, -1), 8),
             ('BOX', (0, 0), (-1, -1), 0.2, self.BLUE_ULL),
             ('LINEABOVE', (0, 0), (-1, -1), 0.2, self.BLUE_ULL),
             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
             ('BACKGROUND', (0, 0), (-1, 0), self.BLUE_ULL),
             ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
             ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white,
                                                   self.BLUE_SECONDARY_ULL])]
        )
        return style
