# -*- encoding: UTF-8 -*-

#
#    Copyright 2014-2015
#
#      STIC-Investigación - Universidad de La Laguna (ULL) <gesinv@ull.edu.es>
#
#    This file is part of Portal del Investigador.
#
#    Portal del Investigador is free software: you can redistribute it and/or
#    modify it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    Portal del Investigador is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Portal del Investigador.  If not, see
#    <http://www.gnu.org/licenses/>.
#

from django.conf import settings as st


@classmethod
def get_all(cls, url, use_redis=True, timeout=None):
    if url == st.WS_ULL_LEARNING % 'example_code':
        return [{u'des1_titulacion': u'LICENCIADO EN MATEMATICAS',
                 u'organismo': u'UNIVERSIDAD DE LA LAGUNA',
                 u'f_expedicion': u'18-12-2001',
                 u'des1_grado_titulacion': u'Licenciado/Ingeniero Superior'},
                {u'des1_titulacion': u'Doctor por la Universidad de La Laguna',
                 u'organismo': u'UNIVERSIDAD DE LA LAGUNA',
                 u'f_expedicion': u'07-07-2006',
                 u'des1_grado_titulacion': u'Doctor'}]
    elif url == st.WS_ULL_CARGOS % 'example_code':
        return [{u'dedicacion': u'Tiempo Completo',
                 u'des1_cargo': u'SECRETARIO DPTO ANALISIS MATEMATICO',
                 u'centro': u'DPTO.ANALISIS MATEMATICO',
                 u'departamento': u'AN\xc1LISIS MATEM\xc1TICO',
                 u'f_hasta': u'13-02-2013', u'f_toma_posesion': u'30-11-2010'}]


@classmethod
def get_learning(cls, url, use_redis=True, timeout=None):
    if url == st.WS_ULL_LEARNING % 'example_code':
        return [{u'des1_titulacion': u'LICENCIADO EN MATEMATICAS',
                 u'organismo': u'UNIVERSIDAD DE LA LAGUNA',
                 u'f_expedicion': u'18-12-2001',
                 u'des1_grado_titulacion': u'Licenciado/Ingeniero Superior'},
                {u'des1_titulacion': u'Doctor por la Universidad de La Laguna',
                 u'organismo': u'UNIVERSIDAD DE LA LAGUNA',
                 u'f_expedicion': u'07-07-2006',
                 u'des1_grado_titulacion': u'Doctor'}]
    else:
        return []


@classmethod
def get_learning_no_organismo(cls, url, use_redis=True, timeout=None):
    if url == st.WS_ULL_LEARNING % 'example_code':
        return [{u'des1_titulacion': u'LICENCIADO EN BELLAS ARTES',
                 u'f_expedicion': u'04-11-1965',
                 u'des1_grado_titulacion': u'Licenciado/Ingeniero Superior'}]
    else:
        return []


@classmethod
def get_learning_no_f_expedicion(cls, url, use_redis=True, timeout=None):
    if url == st.WS_ULL_LEARNING % 'example_code':
        return [{u'des1_titulacion': u'LICENCIADO EN FILOSOFIA'
                                     u' Y CIENCIAS DE LA EDUCACION',
                 u'organismo': u'UNIV. BARCELONA',
                 u'des1_grado_titulacion': u'Licenciado/Ingeniero Superior'}]
    else:
        return []


@classmethod
def get_learning_doctor_no_organismo(cls, url, use_redis=True, timeout=None):
    if url == st.WS_ULL_LEARNING % 'example_code':
        return [{u'des1_titulacion': u'LICENCIADO EN BELLAS ARTES',
                 u'f_expedicion': u'04-11-1965',
                 u'des1_grado_titulacion': u'Doctor'}]
    else:
        return []


@classmethod
def get_learning_doctor_no_f_expedicion(cls, url, use_redis=True, timeout=None):
    if url == st.WS_ULL_LEARNING % 'example_code':
        return [{u'des1_titulacion': u'LICENCIADO EN FILOSOFIA'
                                     u' Y CIENCIAS DE LA EDUCACION',
                 u'organismo': u'UNIV. BARCELONA',
                 u'des1_grado_titulacion': u'Doctor'}]
    else:
        return []


@classmethod
def get_cargos(cls, url, use_redis=True, timeout=None):
    if url == st.WS_ULL_CARGOS % 'example_code':
        return [{u'dedicacion': u'Tiempo Completo',
                 u'des1_cargo': u'SECRETARIO DPTO ANALISIS MATEMATICO',
                 u'centro': u'DPTO.ANALISIS MATEMATICO',
                 u'departamento': u'AN\xc1LISIS MATEM\xc1TICO',
                 u'f_hasta': u'13-02-2013', u'f_toma_posesion': u'30-11-2010'}]
    else:
        return []


@classmethod
def get_cargos_no_f_hasta(cls, url, use_redis=True, timeout=None):
    if url == st.WS_ULL_CARGOS % 'example_code':
        return [{u'dedicacion': u'Tiempo Completo',
                 u'des1_cargo': u'SUBDIRECTOR DPTO FILOLOGIA MODERNA',
                 u'centro': u'DPTO.FILOLOGIA MODERNA',
                 u'departamento': u'FILOLOGÍA FRANCESA Y ROMÁNICA',
                 u'f_toma_posesion': u'29-01-1996'}]
    else:
        return []


@classmethod
def get_cargos_no_departamento(cls, url, use_redis=True, timeout=None):
    if url == st.WS_ULL_CARGOS % 'example_code':
        return [{u'dedicacion': u'Tiempo Completo',
                 u'des1_cargo': u'DIRECTOR OFICINA TRANSF.RESUL.INVEST',
                 u'centro': u'VICERRECTORADO INVEST,DESAR TECNOL E INN',
                 u'f_toma_posesion': u'08-05-2000', u'f_hasta': u'06-01-2003'}]
    else:
        return []


@classmethod
def get_cargos_no_dedicacion(cls, url, use_redis=True, timeout=None):
    if url == st.WS_ULL_CARGOS % 'example_code':
        return [{u'des1_cargo': u'DIRECTOR ETS. INGENIERIA CIVIL E INDUS',
                 u'centro': u'E.U. ENFERMERIA Y FISIOTERAPIA',
                 u'departamento': u'ECONOMÍA APLICADA',
                 u'f_toma_posesion': u'08-05-2000', u'f_hasta': u'01-09-2004'}]
    else:
        return []