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

import suds
import base64
import logging

logger = logging.getLogger('cvn')


def pdf2xml(pdf, name):
    content = base64.encodestring(pdf)
    # Web Service - FECYT
    client_ws = suds.client.Client(st_cvn.WS_FECYT_PDF2XML)
    try:
        result_xml = client_ws.service.cvnPdf2Xml(
            st_cvn.FECYT_USER, st_cvn.FECYT_PASSWORD, content)
    except:
        logger.warning(
            u'No hay respuesta del WS' +
            u' de la FECYT para el fichero' +
            u' %s' % name)
        return False, 1
    # Format CVN-XML of FECYT
    if result_xml.errorCode == 0:
        return base64.decodestring(result_xml.cvnXml), 0
    return False, result_xml.errorCode


def xml2pdf(xml):
    content = xml.decode('utf8')
    # Web Service - FECYT
    client_ws = suds.client.Client(st_cvn.WS_FECYT_XML2PDF)
    try:
        pdf = client_ws.service.crearPDFBean(
            st_cvn.FECYT_USER, st_cvn.FECYT_PASSWORD,
            st_cvn.FECYT_CVN_NAME, content, st_cvn.FECYT_TIPO_PLANTILLA)
    except UnicodeDecodeError as e:
        logger.error(e.message)
        return None
    if pdf.returnCode == '01':
        xml_error = base64.decodestring(pdf.dataHandler)
        logger.error(st_cvn.RETURN_CODE[pdf.returnCode] + u'\n' +
                     xml_error.decode('iso-8859-10'))
        return None
    return base64.decodestring(pdf.dataHandler)
