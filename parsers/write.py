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
from lxml import etree

import datetime
import time


def get_xml_fragment(filepath):
    xml = open(filepath)
    content = xml.read()
    xml.close()
    return content


class CvnXmlWriter:

    DATE_FORMAT = st_cvn.CVN_XML_DATE_FORMAT

    def __init__(self, user, *args, **kwargs):
        xml = kwargs.pop('xml', None)
        if xml is not None:
            self.xml = etree.fromstring(xml)
            self.xml.find(
                'Version/VersionID/Date/Item'
            ).text = time.strftime(self.DATE_FORMAT)
        else:
            if user.profile.documento[0].isdigit():
                documento = st_cvn.OfficialId.DNI
            else:
                documento = st_cvn.OfficialId.NIE
            xml = get_xml_fragment(st_cvn.XML_SKELETON_PATH) % {
                'today': time.strftime(self.DATE_FORMAT),
                'version': st_cvn.WS_FECYT_VERSION,
                'given_name': user.first_name,
                'first_family_name': user.last_name,
                'id_type': documento.name,
                'id_type_code': documento.value,
                'official_id': user.profile.documento,
                'internet_email_address': user.email
            }
            self.xml = etree.fromstring(xml.encode('utf8'))

    def tostring(self):
        return etree.tostring(self.xml)

    def _get_code(self, dic, key):
        if key is None:
            return None
        try:
            code = dic[key.upper()]
        except KeyError:
            code = u'OTHERS'
        return code

    def _remove_node(self, xml, node):
        node = xml.find(node)
        xml.remove(node)

    def _remove_child_node(self, xml, parent, child):
        node = xml.xpath("%s/%s" % (parent, child))[0]
        node.getparent().remove(node)

    def _remove_child_node_by_code(self, xml, parent, child, code):
        node = xml.xpath('%s/%s[@code="%s"]' % (parent, child, code))[0]
        node.getparent().remove(node)

    def _remove_parent_node_by_code(self, xml, node, code):
        nodes = xml.xpath('//%s[@code="%s"]' % (node, code))
        if len(nodes):
            node = nodes[0].getparent()
            xml.remove(node)

    def add_teaching(self, curso_inicio, creditos, asignatura=None, curso=None,
                     plan_nomid=None, departamento=None, centro_nomid=None,
                     categ_anyo=None, tipologia=None, tipo_estudio=None,
                     university=st_cvn.UNIVERSITY):
        """Graduate, postgraduate (bachelor's degree, master, engineering)"""
        program_code = self._get_code(st_cvn.PROGRAM_TYPE, tipo_estudio)
        subject_code = self._get_code(st_cvn.SUBJECT_TYPE, tipologia)
        teaching = etree.fromstring(
            get_xml_fragment(st_cvn.XML_TEACHING) % {
                'subject': asignatura,
                'professional_category': categ_anyo,
                'program_type': program_code,
                'program_others': tipo_estudio,
                'subject_type': subject_code,
                'subject_others': tipologia,
                'course': curso,
                'qualification': plan_nomid,
                'department': departamento,
                'faculty': centro_nomid,
                'school_year': curso_inicio,
                'number_credits': creditos,
                'university': university,
            }
        )

        if asignatura is None:
            self._remove_node(xml=teaching, node='Title')

        if categ_anyo is None:
            self._remove_node(xml=teaching, node='Description')

        if tipo_estudio is None:
            self._remove_parent_node_by_code(
                xml=teaching, node='Type', code='030.010.000.140')

        if tipo_estudio is not None and program_code != u'OTHERS':
            self._remove_child_node_by_code(
                xml=teaching, parent='Filter',
                child='Others', code=st_cvn.PROGRAM_TYPE_OTHERS)

        if tipologia is None:
            self._remove_parent_node_by_code(
                xml=teaching, node='Type', code='030.010.000.190')

        if tipologia is not None and subject_code != u'OTHERS':
            self._remove_child_node_by_code(
                xml=teaching, parent='Filter',
                child='Others', code=st_cvn.SUBJECT_TYPE_OTHERS)

        if curso is None:
            self._remove_node(xml=teaching, node='Edition')

        if plan_nomid is None:
            self._remove_node(xml=teaching, node='Link')

        if not creditos:
            self._remove_node(xml=teaching, node='PhysicalDimension')

        if university is None:
            self._remove_parent_node_by_code(
                xml=teaching, node='EntityName',
                code=st_cvn.Entity.UNIVERSITY.value)

        if departamento is None:
            self._remove_parent_node_by_code(
                xml=teaching, node='EntityName',
                code=st_cvn.Entity.TEACHING_DEPARTAMENT.value)

        if centro_nomid is None:
            self._remove_parent_node_by_code(
                xml=teaching, node='EntityName',
                code=st_cvn.Entity.FACULTY.value)

        self.xml.append(teaching)

    def add_learning(self, des1_titulacion, des1_grado_titulacion,
                     organismo=None, f_expedicion=None):
        titulacion_code = self._get_code(
            st_cvn.OFFICIAL_TITLE_TYPE, des1_grado_titulacion.upper())
        learning = etree.fromstring(
            get_xml_fragment(st_cvn.XML_LEARNING) % {
                'title': des1_titulacion,
                'title_code': titulacion_code,
                'university': organismo,
                'date': f_expedicion.strftime(
                    self.DATE_FORMAT) if f_expedicion else None,
                'others': des1_grado_titulacion,
            }
        )

        if f_expedicion is None:
            self._remove_node(learning, 'Date')

        if organismo is None:
            self._remove_node(learning, 'Entity')

        if titulacion_code != u'OTHERS':
            self._remove_child_node(
                xml=learning, parent='Filter', child='Others')

        self.xml.append(learning)

    def add_learning_phd(self, des1_titulacion, f_expedicion=None,
                         organismo=st_cvn.UNIVERSITY):
        """ PhD (Doctor) """
        learning_phd = etree.fromstring(
            get_xml_fragment(st_cvn.XML_LEARNING_PHD) % {
                'title': des1_titulacion,
                'university': organismo,
                'date': f_expedicion.strftime(
                    self.DATE_FORMAT) if f_expedicion else None,
            }
        )

        if f_expedicion is None:
            self._remove_node(learning_phd, 'Date')

        if organismo is None:
            self._remove_node(learning_phd, 'Entity')

        self.xml.append(learning_phd)

    def add_profession(self, employer=st_cvn.UNIVERSITY,
                       des1_cargo=None, f_toma_posesion=None,
                       des1_cce=None, f_desde=None,
                       f_hasta=None, centro=None, departamento=None,
                       dedicacion=None):

        values = {'employer': employer,
                  'centre': centro,
                  'department': departamento,
                  'dedication_code': None,
                  'dedication_type': None,
                  }

        if des1_cargo is not None:
            values['title'] = des1_cargo
        elif des1_cce is not None:
            values['title'] = des1_cce

        if f_toma_posesion is not None:
            values['start_date'] = f_toma_posesion.strftime(self.DATE_FORMAT)
        elif f_desde is not None:
            values['start_date'] = f_desde.strftime(self.DATE_FORMAT)

        if dedicacion is not None:
            values['dedication_code'] = (
                st_cvn.ProfessionCode.CURRENT_TRIMMED.value
                if f_hasta is None else
                st_cvn.ProfessionCode.OLD_TRIMMED.value)
            values['dedication_type'] = (
                st_cvn.DedicationType.TOTAL.value
                if dedicacion else
                st_cvn.DedicationType.PARTIAL.value)

        xml = st_cvn.XML_CURRENT_PROFESSION
        if f_hasta is not None:
            values['end_date'] = f_hasta.strftime(self.DATE_FORMAT)
            xml = st_cvn.XML_PROFESSION

        profession = etree.fromstring(get_xml_fragment(xml) % values)

        if centro is None:
            centre_code = (st_cvn.Entity.CURRENT_CENTRE.value
                           if f_hasta is None else
                           st_cvn.Entity.CENTRE.value)
            self._remove_parent_node_by_code(
                xml=profession, node='EntityName', code=centre_code)

        if departamento is None:
            department_code = (st_cvn.Entity.CURRENT_DEPT.value
                               if f_hasta is None else
                               st_cvn.Entity.DEPT.value)
            self._remove_parent_node_by_code(
                xml=profession, node='EntityName', code=department_code)

        if dedicacion is None:
            self._remove_node(xml=profession, node='Dedication')

        self.xml.append(profession)
