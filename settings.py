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

from datetime import date
from django.conf import settings as st
from enum import IntEnum, Enum

import datetime
import os

# Enable translations in this file
_ = lambda s: s

# DJANGO CONSTANCE
st.CONSTANCE_CONFIG['EXPIRY_DATE'] = (
    datetime.date(2013, 12, 31), _("Expiry date for a CVN"))

# Default Entity
UNIVERSITY = "Universidad de la Laguna"

# ******************************* PATHS *************************************
FILE_TEST_ROOT = os.path.join(st.BASE_DIR, 'cvn/tests/files/')
MIGRATION_ROOT = os.path.join(st.BASE_DIR, 'importCVN')
XML_TEMPLATE = os.path.join(st.BASE_DIR, 'cvn/templates/cvn/xml')
# ******************************* PATHS *************************************

# ******************************* TESTS *************************************
CVN_VERS_TEST = '1.3'
# ******************************* TESTS *************************************

# ******************************* XML FILES *********************************
XML_SKELETON_PATH = os.path.join(XML_TEMPLATE, 'skeleton.xml')
XML_CURRENT_PROFESSION = os.path.join(XML_TEMPLATE, 'current_profession.xml')
XML_PROFESSION = os.path.join(XML_TEMPLATE, 'profession.xml')
XML_TEACHING = os.path.join(XML_TEMPLATE, 'teaching.xml')
XML_LEARNING = os.path.join(XML_TEMPLATE, 'learning.xml')
XML_LEARNING_PHD = os.path.join(XML_TEMPLATE, 'learning_phd.xml')
# ******************************* XML FILES *********************************

# ******************************* URLS **************************************
EDITOR_FECYT = 'https://cvn.fecyt.es/editor/'
# ******************************* URLS **************************************


# ******************************* CVN STATUS ********************************
class CVNStatus(IntEnum):
    UPDATED = 0
    EXPIRED = 1
    INVALID_IDENTITY = 2

CVN_STATUS = (
    (CVNStatus.UPDATED.value, _("Updated")),
    (CVNStatus.EXPIRED.value, _("Expired")),
    (CVNStatus.INVALID_IDENTITY.value, _("Invalid Identity")),
)
# ******************************* CVN STATUS ********************************

# ******************************* CVN WAITING *******************************
# Messages of waiting when be upload a new CVN
MESSAGES_WAITING = {
    0: _(u"This process may take several minutes, please wait."),
    1: _(u"Connection has been established with the FECYT. Your CVN is being processed, "
         u"please wait."),
    2: _(u"Verifying CVN details, please wait."),
    3: _(u"This process is taking longer than usual, please wait. If an error occurs "
         u"try again. If the error persists contact the %(support)s (%(email)s).")
}

TIME_WAITING = 5000  # In milliseconds
# ******************************* CVN WAITING ********************************

# ******************************* WS FECYT **********************************
FECYT_USER = '<user>'
FECYT_PASSWORD = '<password>'
WS_FECYT_PDF2XML = "https://www.cvnet.es/cvn2RootBean_v1_3/services/Cvn2RootBean?wsdl"
WS_FECYT_XML2PDF = "https://www.cvnet.es/generadorPdfWS_v1_3/services/GenerarPDFWS?wsdl"
WS_FECYT_VERSION = "1.3.0"
FECYT_CVN_NAME = 'CVN'
FECYT_TIPO_PLANTILLA = 'PN2008'
CVN_XML_DATE_FORMAT = '%Y-%m-%d'
# ******************************* WS FECYT **********************************

# ******************************* FECYT ERRORS ******************************
ERROR_CODES = {
    1: _("General error not determined in FECYT server."),
    2: _("The PDF has no associated XML."),
    3: _(u'The user that is intended to import does not exist in the database'
         u' FECYT.'),
    4: _("Incorrect password."),
    5: _(u'The Web Service can not connect to the database FECYT '
         u'institutions.'),
    6: _(u'Error not determined during the authentication process with FECYT.'),
    8: _("Imports are not permitted for this institution."),
    10: _("The CvnRootBean obtained from XML or PDF is invalid."),
    13: _("The CVN-XML is invalid."),
    14: _("Failure CvnRootBean extraction from XML."),
    16: _("The XML is empty."),
    17: _(u'The conversion process from 1.2.5 to 1.3.0 CvnRootBean failed.')
}
# ******************************* FECYT ERRORS ******************************

# ******************************* FECYT RETURN CODE *************************
RETURN_CODE = {
    '00': _("CVN-PDF generated correctly"),
    '01': _("Failed to generate CVN-PDF")
}
# ******************************* FECYT RETURN CODE *************************

# ******************************* CVN ITEMS *********************************


class CvnItemCode(Enum):
    # Professional activity
    PROFESSION_CURRENT = '010.010.000.000'
    PROFESSION_FORMER = '010.020.000.000'
    # Learning activity
    LEARNING_DEGREE = '020.010.010.000'
    LEARNING_PHD = '020.010.020.000'
    LEARNING_OTHER = '020.050.000.000'
    # Teaching activity
    TEACHING_SUBJECT = '030.010.000.000'
    TEACHING_PHD = '030.040.000.000'                # Model TesisDoctoral
    # Scientific experience
    SCIENTIFICEXP_PROJECT = '050.020.010.000'       # Model Proyecto
    SCIENTIFICEXP_AGREEMENT = '050.020.020.000'     # Model Convenio
    SCIENTIFICEXP_PROPERTY = '050.030.010.000'      # Model Patente
    # Scientific activity
    SCIENTIFICACT_PRODUCTION = '060.010.010.000'    # Model Publicacion
    SCIENTIFICACT_CONGRESS = '060.010.020.000'      # Model Congreso

# CvnItem > CvnItemID > CVNPF > Item
CVNITEM_CODE = {
    # Actividad científica y tecnológica
    u"060.010.010.000": u'Publicacion',
    u"060.010.020.000": u'Congreso',
    # Experiencia científica y tecnológica
    u"050.020.010.000": u'Proyecto',
    u"050.020.020.000": u'Convenio',
    u"050.030.010.000": u'Patente',
    # Actividad docente
    u"030.040.000.000": u'TesisDoctoral',
}

# CvnItem > Subtype > SubType1 > Item
CVNITEM_SUBTYPE_CODE = {
    u'035': u'Articulo',
    u'148': u'Capitulo',
    u'112': u'Libro',
    u'100': u'TesisDoctoral',
}

REGULAR_DATE_CODE = '040'


# Agent > Identificacion > Personal Identification > OfficialId
class OfficialId(Enum):
    DNI = '000.010.000.100'
    NIE = '000.010.000.110'

# ExternalPK > Type > Item
PRODUCTION_ID_CODE = {
    'FINANCIADORA': '000',
    'ISSN': '010',
    'ISBN': '020',
    'DEPOSITO_LEGAL': '030',
    'SOLICITUD': '060',
}

# Place > CountryCode > Item
PRIORITY_COUNTRY = "050.030.010.120"
EXTENDED_COUNTRY = "050.030.010.220"


# Entity > EntityName code
class Entity(Enum):
    CURRENT_EMPLOYER = "010.010.000.020"
    CURRENT_CENTRE = "010.010.000.060"
    CURRENT_DEPT = "010.010.000.080"
    EMPLOYER = "010.020.000.020"
    CENTRE = "010.020.000.060"
    DEPT = "010.020.000.080"
    UNIVERSITY = "030.010.000.080"
    TEACHING_DEPARTAMENT = "030.010.000.130"
    FACULTY = "030.010.000.540"
    PHD_UNIVERSITY = "030.040.000.080"
    OPERATOR = "050.030.010.250"
    OWNER = "050.030.010.300"


OFFICIAL_TITLE_TYPE = {
    u"DOCTOR": u'940',
    u"LICENCIADO/INGENIERO SUPERIOR": u'950',
    u"DIPLOMADO/INGENIERO TECNICO": u'960'
}

# Indicates 'Link' node contains Congreso data
DATA_CONGRESO = u"110"

# FECYT codes for economic information
ECONOMIC_DIMENSION = {
    # Proyectos
    u"050.020.010.290": u'cuantia_total',
    u"050.020.010.300": u'cuantia_subproyecto',
    u"050.020.010.310": u'porcentaje_en_subvencion',
    u"050.020.010.320": u'porcentaje_en_credito',
    u"050.020.010.330": u'porcentaje_mixto',
    # Convenios
    u"050.020.020.200": u'cuantia_total',
    u"050.020.020.210": u'cuantia_subproyecto',
    u"050.020.020.220": u'porcentaje_en_subvencion',
    u"050.020.020.230": u'porcentaje_en_credito',
    u"050.020.020.240": u'porcentaje_mixto',
}

# Scope for Congresos, Proyectos, Convenios
SCOPE = {
    u"000": u"Autonómica",
    u"010": u"Nacional",
    u"020": u"Unión Europea",
    u"030": u"Internacional no UE",
    u"OTHERS": u"Otros",
}


class ProfessionCode(Enum):
    CURRENT = '010'
    OLD = '020'
    CURRENT_TRIMMED = '10'
    OLD_TRIMMED = '20'


class DedicationType(Enum):
    TOTAL = '020'
    PARTIAL = '030'


class FilterCode(Enum):
    PROGRAM = "030.010.000.140"
    SUBJECT = "030.010.000.190"

PROGRAM_TYPE = {
    u"ARQUITECTO": u"020",
    u"ARQUITECTO TÉCNICO": u"030",
    u"DIPLOMADO/MAESTRO": u"240",
    u"DOCTORADO": u"250",
    u"INGENIERO": u"420",
    u"INGENIERO TÉCNICO": u"430",
    u"LICENCIADO": u"470",
    u"MÁSTER OFICIAL": u"480",
}
PROGRAM_TYPE_OTHERS = "030.010.000.150"

SUBJECT_TYPE = {
    u"TRONCAL": u"000",
    u"OBLIGATORIA": u"010",
    u"OPTATIVA": u"020",
    u"LIBRE CONFIGURACION": u"030",
    u"DOCTORADO": u"050",
}
SUBJECT_TYPE_OTHERS = "030.010.000.430"

# ******************************* CVN ITEMS *********************************

RANGE_OF_YEARS = (1950, date.today().year + 1)  # Range of years for CVN Export

# Unauthorized CVN Authors
CVN_PDF_AUTHOR_NOAUT = [u'FECYT - Author of Example', ]

# HISTORICAL REPORT
UNIVERSITY_REPORT_DB = '2013'


# ************************* REPORTS *******************************************

class REPORTS_DIRECTORY(Enum):
    DEPT = 'department'
    AREA = 'area'
    USERS = 'users'

# Paths
REPORTS_IPDF_PATH = 'reports/ipdf'
REPORTS_RCSV_PATH = 'reports/rcsv'
REPORTS_ICSV_PATH = 'reports/icsv'
REPORTS_IMAGES = os.path.join(st.STATIC_ROOT, 'images/')

# Fields on the csv file of informe_csv (dept_report and list_report management commands)
INFORME_CSV_FIELDS_ARTICULO = [
    'titulo', 'nombre_publicacion', 'fecha', 'autores', 'volumen', 'numero',
    'pagina_inicial', 'pagina_final', 'issn', 'isbn', 'deposito_legal'
]

INFORME_CSV_FIELDS_CAPITULO = [
    'titulo', 'nombre_publicacion', 'fecha', 'autores', 'volumen', 'numero',
    'pagina_inicial', 'pagina_final', 'issn', 'isbn', 'deposito_legal'
]

INFORME_CSV_FIELDS_LIBRO = [
    'titulo', 'nombre_publicacion', 'fecha', 'autores', 'volumen', 'numero',
    'pagina_inicial', 'pagina_final', 'issn', 'isbn', 'deposito_legal'
]

INFORME_CSV_FIELDS_CONGRESO = [
    'titulo', 'nombre_del_congreso', 'ciudad_de_realizacion', 'fecha',
    'fecha_de_inicio', 'fecha_de_fin', 'autores', 'ambito', 'otro_ambito',
    'deposito_legal', 'publicacion_acta_congreso'
]

INFORME_CSV_FIELDS_CONVENIO = [
    'titulo', 'numero_de_investigadores', 'autores', 'fecha_de_inicio',
    'fecha_de_fin', 'duracion', 'ambito', 'otro_ambito',
    'cod_segun_financiadora', 'cuantia_total', 'cuantia_subproyecto',
    'porcentaje_en_subvencion', 'porcentaje_en_credito', 'porcentaje_mixto'
]

INFORME_CSV_FIELDS_PROYECTO = [
    'titulo', 'numero_de_investigadores', 'autores', 'fecha_de_inicio',
    'fecha_de_fin', 'duracion', 'ambito', 'otro_ambito',
    'cod_segun_financiadora', 'cuantia_total', 'cuantia_subproyecto',
    'porcentaje_en_subvencion', 'porcentaje_en_credito', 'porcentaje_mixto'
]

INFORME_CSV_FIELDS_TESIS = [
    'titulo', 'fecha', 'autor', 'universidad_que_titula', 'codirector'
]

INFORME_CSV_FIELDS_PATENTE = [
    'titulo', 'fecha', 'fecha_concesion', 'num_solicitud', 'lugar_prioritario',
    'lugares', 'entidad_titular', 'empresas'
]
# ************************* REPORTS *******************************************

# ************************* SETTINGS LOCAL ***********************************
try:
    CVN_SETTINGS_LOCAL
except NameError:
    try:
        from .settings_local import *
    except ImportError:
        pass
# ************************* SETTINGS LOCAL ***********************************
