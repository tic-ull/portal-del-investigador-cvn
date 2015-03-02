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

from read_helpers import (parse_date_interval, parse_dedication_type,
                          parse_entities, parse_title, parse_authors,
                          parse_economic, parse_scope, parse_produccion_id,
                          parse_date, parse_publicacion_location, parse_places,
                          parse_filters)
from cvn import settings as st_cvn


def _parse_cvnitem_profession(node):
    """Shared parser for current and old profession"""
    date = parse_date_interval(node.find('Date'))
    item = {
        u'des1_cargo': unicode(node.find('Title/Name/Item').text),
        u'f_toma_posesion': date[0],
        u'f_hasta': date[1],
    }

    dedicacion = parse_dedication_type(node.find('Dedication/Item'))
    if dedicacion is not None:
        item[u'dedicacion'] = dedicacion

    entities = parse_entities(node.findall('Entity'))

    item[u'employer'] = unicode(
        entities[st_cvn.Entity.EMPLOYER.value]
        if entities[st_cvn.Entity.EMPLOYER.value] is not None
        else entities[st_cvn.Entity.CURRENT_EMPLOYER.value])

    if entities[st_cvn.Entity.CENTRE.value] is not None:
        item[u'centro'] = entities[st_cvn.Entity.CENTRE.value]
    elif entities[st_cvn.Entity.CURRENT_CENTRE.value] is not None:
        item[u'centro'] = entities[st_cvn.Entity.CURRENT_CENTRE.value]

    if entities[st_cvn.Entity.DEPT.value] is not None:
        item[u'departamento'] = entities[st_cvn.Entity.DEPT.value]
    elif entities[st_cvn.Entity.CURRENT_DEPT.value] is not None:
        item[u'departamento'] = entities[st_cvn.Entity.CURRENT_DEPT.value]

    return item


def _parse_cvnitem_scientificexp(node):
    """Shared parser for project and agreement"""
    date_node = node.find('Date')
    date = parse_date_interval(date_node)

    item = {'titulo': parse_title(node),
            'fecha_de_inicio': date[0],
            'fecha_de_fin': date[1],
            'duracion': date[2],
            'autores': parse_authors(node.findall('Author'))}

    item.update(parse_economic(node.findall('EconomicDimension')))
    if node.find('ExternalPK/Code'):
        item[u'cod_segun_financiadora'] = unicode(node.find(
            'ExternalPK/Code/Item').text.strip())
    item.update(parse_scope(node.find('Scope')))
    return item


def parse_cvnitem_scientificexp_project(node):
    return _parse_cvnitem_scientificexp(node)


def parse_cvnitem_scientificexp_agreement(node):
    return _parse_cvnitem_scientificexp(node)


def parse_cvnitem_scientificact_production(node):
    pids = parse_produccion_id(node.findall('ExternalPK'))
    item = {
        'titulo': parse_title(node),
        'autores': parse_authors(node.findall('Author')),
        'fecha': parse_date(node.find('Date')),
        'issn': pids[st_cvn.PRODUCTION_ID_CODE['ISSN']],
        'isbn': pids[st_cvn.PRODUCTION_ID_CODE['ISBN']],
        'deposito_legal': pids[st_cvn.PRODUCTION_ID_CODE['DEPOSITO_LEGAL']]
    }
    if (node.find('Link/Title/Name') and
            node.find('Link/Title/Name/Item').text):
        item[u'nombre_publicacion'] = unicode(node.find(
            'Link/Title/Name/Item').text.strip())
    item.update(parse_publicacion_location(node.find('Location')))

    return item


def parse_cvnitem_scientificact_congress(node):
    item = {'titulo': parse_title(node),
            'autores': parse_authors(node.findall('Author'))}

    for itemXML in node.findall('Link'):
        if itemXML.find(
            'CvnItemID/CodeCVNItem/Item'
        ).text.strip() == st_cvn.DATA_CONGRESO:
            if (itemXML.find('Title/Name') and
                    itemXML.find('Title/Name/Item').text):
                item[u'nombre_del_congreso'] = unicode(itemXML.find(
                    'Title/Name/Item').text.strip())

            date_node = itemXML.find('Date')
            (item['fecha_de_inicio'], item['fecha_de_fin'],
                duracion) = parse_date_interval(date_node)

            if itemXML.find('Place/City'):
                item[u'ciudad_de_realizacion'] = unicode(itemXML.find(
                    'Place/City/Item').text.strip())
            # Ámbito
            item.update(parse_scope(itemXML.find('Scope')))
    return item


def parse_cvnitem_scientificexp_property(node):

    places = parse_places(node.findall("Place"))
    entities = parse_entities(node.findall("Entity"))
    num_solicitud = parse_produccion_id(
        node.findall('ExternalPK'))[st_cvn.PRODUCTION_ID_CODE['SOLICITUD']]
    item = {'titulo': parse_title(node),
            'num_solicitud': num_solicitud,
            'lugar_prioritario': places[0],
            'lugares': places[1],
            'autores': parse_authors(node.findall('Author')),
            'entidad_titular': entities[st_cvn.Entity.OWNER.value],
            'empresas': entities[st_cvn.Entity.OPERATOR.value]}

    dates = node.findall('Date')
    for date in dates:                              # There can be 2 dates
        parsed_date = parse_date(date)
        date_type = date.find("Moment/Item").text
        if date_type == st_cvn.REGULAR_DATE_CODE:   # Date of request
            item['fecha'] = parsed_date
        else:                                       # And date of granting
            item['fecha_concesion'] = parsed_date

    return item


def parse_cvnitem_profession_current(node):
    return _parse_cvnitem_profession(node)


def parse_cvnitem_profession_former(node):
    return _parse_cvnitem_profession(node)


def parse_cvnitem_teaching_phd(node):
    entities = parse_entities(node.findall('Entity'))
    item = {'titulo': parse_title(node),
            'autor': parse_authors(node.findall('Author')),
            'codirector': parse_authors(node.findall('Link/Author')),
            'fecha': parse_date(node.find('Date')),
            'universidad_que_titula': entities[
                st_cvn.Entity.PHD_UNIVERSITY.value]}
    return item


def parse_cvnitem_teaching_subject(node):

    entities = parse_entities(node.findall('Entity'))
    filters = parse_filters(node.findall('Filter'))
    item = {
        'asignatura': node.find('Title/Name/Item').text,
        'curso': node.find('Edition/Text/Item').text,
        'plan_nomid': node.find('Link/Title/Name/Item').text,
        'curso_inicio': node.find('Date/StartDate/Year/Item').text,
        'creditos': node.find('PhysicalDimension/Value/Item').text,
        'university': entities[st_cvn.Entity.UNIVERSITY.value],
        'departamento': entities[st_cvn.Entity.TEACHING_DEPARTAMENT.value],
        'centro_nomid': entities[st_cvn.Entity.FACULTY.value],
        'tipo_estudio': filters[st_cvn.FilterCode.PROGRAM.value],
        'tipologia': filters[st_cvn.FilterCode.SUBJECT.value]
    }

    professional_category = node.find('Description/Item').text
    if professional_category is not None:
        item['categ_anyo'] = professional_category

    return item


def parse_cvnitem_learning_phd(node):
    organismo = node.find('Entity/EntityName/Item')
    item = {u'des1_titulacion': unicode(node.find('Title/Name/Item').text),
            u'organismo': unicode(
                organismo.text) if organismo is not None else None,
            u'f_expedicion': parse_date(node.find('Date'))}
    return item


def parse_cvnitem_learning_degree(node):
    des1_grado_titulacion = node.find('Filter/Value/Item').text
    if des1_grado_titulacion == 'OTHERS':
        des1_grado_titulacion = node.find('Filter/Others/Item').text
    else:
        des1_grado_titulacion = st_cvn.OFFICIAL_TITLE_TYPE.keys()[
            st_cvn.OFFICIAL_TITLE_TYPE.values().index(
                unicode(des1_grado_titulacion))]
    item = {u'des1_titulacion': unicode(node.find('Title/Name/Item').text),
            u'des1_grado_titulacion': des1_grado_titulacion,
            u'f_expedicion': parse_date(node.find('Date'))}
    organismo = node.find('Entity/EntityName/Item')
    if organismo is not None:
        item[u'organismo'] = unicode(organismo.text)
    return item


def parse_cvnitem(node):
    cvn_key = node.find('CvnItemID/CVNPK/Item').text.strip()
    cvnitem = None
    if cvn_key == st_cvn.CvnItemCode.PROFESSION_CURRENT.value:
        cvnitem = parse_cvnitem_profession_current(node)
    elif cvn_key == st_cvn.CvnItemCode.PROFESSION_FORMER.value:
        cvnitem = parse_cvnitem_profession_former(node)
    elif cvn_key == st_cvn.CvnItemCode.LEARNING_PHD.value:
        cvnitem = parse_cvnitem_learning_phd(node)
    elif cvn_key == st_cvn.CvnItemCode.TEACHING_SUBJECT.value:
        cvnitem = parse_cvnitem_teaching_subject(node)
    elif cvn_key == st_cvn.CvnItemCode.LEARNING_DEGREE.value:
        cvnitem = parse_cvnitem_learning_degree(node)
    elif cvn_key == st_cvn.CvnItemCode.SCIENTIFICEXP_PROPERTY.value:
        cvnitem = parse_cvnitem_scientificexp_property(node)
    elif cvn_key == st_cvn.CvnItemCode.SCIENTIFICEXP_AGREEMENT.value:
        cvnitem = parse_cvnitem_scientificexp_agreement(node)
    elif cvn_key == st_cvn.CvnItemCode.SCIENTIFICEXP_PROJECT.value:
        cvnitem = parse_cvnitem_scientificexp_project(node)
    elif cvn_key == st_cvn.CvnItemCode.TEACHING_PHD.value:
        cvnitem = parse_cvnitem_teaching_phd(node)
    elif cvn_key == st_cvn.CvnItemCode.SCIENTIFICACT_CONGRESS.value:
        cvnitem = parse_cvnitem_scientificact_congress(node)
    elif cvn_key == st_cvn.CvnItemCode.SCIENTIFICACT_PRODUCTION.value:
        cvnitem = parse_cvnitem_scientificact_production(node)
    return cvnitem
