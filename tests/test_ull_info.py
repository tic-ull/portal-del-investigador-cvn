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

import os

from django.test import TestCase

from cvn import settings as st_cvn
from core.tests.helpers import init, clean
from core.tests.factories import UserFactory
from mocks.university_info import (
    get_learning, get_all, get_cargos, get_cargos_no_f_hasta,
    get_cargos_no_departamento, get_cargos_no_dedicacion,
    get_learning_no_f_expedicion, get_learning_no_organismo,
    get_learning_doctor_no_f_expedicion, get_learning_doctor_no_organismo,
    get_contratos, get_contratos_no_f_hasta, get_docencia
)

from mock import patch
from core.ws_utils import CachedWS
from cvn.models import CVN
from django.conf import settings as st
from cvn.parsers.read import parse_cvnitem
from cvn.helpers import DateRange
import datetime
from lxml import etree


class UllInfoTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        init()

    def setUp(self):
        self.xml_ull = open(
            os.path.join(st_cvn.FILE_TEST_ROOT, 'xml/CVN-ULL.xml'))
        self.xml_empty = open(
            os.path.join(st_cvn.FILE_TEST_ROOT, 'xml/empty.xml'))
        self.xml_test = open(
            os.path.join(st_cvn.FILE_TEST_ROOT, 'xml/CVN-Test.xml'))

    @patch.object(CachedWS, 'get', get_learning)
    def test_get_pdf_ull_learning(self):
        user = UserFactory.create()
        user.profile.rrhh_code = 'example_code'
        pdf = CVN.get_user_pdf_ull(user=user)
        cvn = CVN(user=user, pdf=pdf)
        cvn.xml_file.open()
        cvn_items = etree.parse(cvn.xml_file).findall('CvnItem')
        ws_content = CachedWS.get(st.WS_ULL_LEARNING % 'example_code')
        for w in ws_content:
            CVN._clean_data_learning(w)
            if u'des1_grado_titulacion' in w:
                w[u'des1_grado_titulacion'] = w[u'des1_grado_titulacion'].upper()
                if w[u'des1_grado_titulacion'] == u'DOCTOR':
                    del w[u'des1_grado_titulacion']
        pdf_content = []
        for item in cvn_items:
            pdf_content.append(parse_cvnitem(item))
        self.assertEqual(len(ws_content), len(pdf_content))
        allequal = True
        for wi in ws_content:
            equal = False
            for pi in pdf_content:
                if cmp(wi, pi) == 0:
                    equal = True
            if not equal:
                allequal = False
        self.assertTrue(allequal)

    @patch.object(CachedWS, 'get', get_cargos)
    def test_get_pdf_ull_cargos(self):
        user = UserFactory.create()
        user.profile.rrhh_code = 'example_code'
        pdf = CVN.get_user_pdf_ull(user=user)
        cvn = CVN(user=user, pdf=pdf)
        cvn.xml_file.open()
        cvn_items = etree.parse(cvn.xml_file).findall('CvnItem')
        ws_content = CachedWS.get(st.WS_ULL_CARGOS % 'example_code')
        for w in ws_content:
            CVN._cleaned_data_profession(w)
            if not u'employer' in w:
                w[u'employer'] = u'Universidad de La Laguna'
        pdf_content = []
        for item in cvn_items:
            pdf_content.append(parse_cvnitem(item))
        self.assertEqual(len(ws_content), len(pdf_content))
        allequal = True
        for wi in ws_content:
            equal = False
            for pi in pdf_content:
                if cmp(wi, pi) == 0:
                    equal = True
            if not equal:
                allequal = False
        self.assertTrue(allequal)

    @patch.object(CachedWS, 'get', get_contratos)
    def test_get_pdf_ull_contratos(self):
        user = UserFactory.create()
        user.profile.rrhh_code = 'example_code'
        pdf = CVN.get_user_pdf_ull(user=user)
        cvn = CVN(user=user, pdf=pdf)
        cvn.xml_file.open()
        cvn_items = etree.parse(cvn.xml_file).findall('CvnItem')
        ws_content = CachedWS.get(st.WS_ULL_CONTRATOS % 'example_code')
        for w in ws_content:
            CVN._cleaned_data_profession(w)
            if not u'employer' in w:
                w[u'employer'] = u'Universidad de La Laguna'
        pdf_content = []
        for item in cvn_items:
            pdf_content.append(parse_cvnitem(item))
        self.assertEqual(len(ws_content), len(pdf_content))
        for pi in pdf_content:
            pi[u'f_desde'] = pi[u'f_toma_posesion']
            del pi[u'f_toma_posesion']
            pi[u'des1_cce'] = pi[u'des1_cargo']
            del pi[u'des1_cargo']
        allequal = True
        for wi in ws_content:
            equal = False
            for pi in pdf_content:
                if cmp(wi, pi) == 0:
                    equal = True
            if not equal:
                allequal = False
        self.assertTrue(allequal)

    @patch.object(CachedWS, 'get', get_docencia)
    def test_get_pdf_ull_teaching(self):
        user = UserFactory.create()
        user.profile.rrhh_code = 'example_code'
        pdf = CVN.get_user_pdf_ull(user=user)
        cvn = CVN(user=user, pdf=pdf)
        cvn.xml_file.open()
        cvn_items = etree.parse(cvn.xml_file).findall('CvnItem')
        ws_content = CachedWS.get(st.WS_ULL_TEACHING % 'example_code')
        for w in ws_content:
            if not u'university' in w:
                w[u'university'] = u'Universidad de La Laguna'
        pdf_content = []
        for item in cvn_items:
            pdf_content.append(parse_cvnitem(item))
        self.assertEqual(len(ws_content), len(pdf_content))
        allequal = True
        for wi in ws_content:
            equal = False
            for pi in pdf_content:
                if cmp(wi, pi) == 0:
                    equal = True
            if not equal:
                allequal = False
        self.assertTrue(allequal)

    def _get_one_cargo_ull(self):
        user = UserFactory.create()
        user.profile.rrhh_code = 'example_code'
        pdf = CVN.get_user_pdf_ull(user=user)
        cvn = CVN(user=user, pdf=pdf)
        cvn.xml_file.open()
        cvn_items = etree.parse(cvn.xml_file).findall('CvnItem')
        self.assertEqual(len(cvn_items), 1)
        item = parse_cvnitem(cvn_items[0])
        ws_content = CachedWS.get(st.WS_ULL_CARGOS % 'example_code')
        self.assertEqual(len(ws_content), 1)
        w = ws_content[0]
        CVN._cleaned_data_profession(w)
        if not u'employer' in w:
            w[u'employer'] = u'Universidad de La Laguna'
        self.assertEqual(cmp(item, w), 0)

    def _get_one_contrato_ull(self):
        user = UserFactory.create()
        user.profile.rrhh_code = 'example_code'
        pdf = CVN.get_user_pdf_ull(user=user)
        cvn = CVN(user=user, pdf=pdf)
        cvn.xml_file.open()
        cvn_items = etree.parse(cvn.xml_file).findall('CvnItem')
        self.assertEqual(len(cvn_items), 1)
        item = parse_cvnitem(cvn_items[0])
        item[u'f_desde'] = item[u'f_toma_posesion']
        del item[u'f_toma_posesion']
        item[u'des1_cce'] = item[u'des1_cargo']
        del item[u'des1_cargo']
        ws_content = CachedWS.get(st.WS_ULL_CONTRATOS % 'example_code')
        self.assertEqual(len(ws_content), 1)
        w = ws_content[0]
        CVN._cleaned_data_profession(w)
        if not u'employer' in w:
            w[u'employer'] = u'Universidad de La Laguna'
        self.assertEqual(cmp(item, w), 0)

    def _get_one_learning_ull(self):
        user = UserFactory.create()
        user.profile.rrhh_code = 'example_code'
        pdf = CVN.get_user_pdf_ull(user=user)
        cvn = CVN(user=user, pdf=pdf)
        cvn.xml_file.open()
        cvn_items = etree.parse(cvn.xml_file).findall('CvnItem')
        self.assertEqual(len(cvn_items), 1)
        item = parse_cvnitem(cvn_items[0])
        ws_content = CachedWS.get(st.WS_ULL_LEARNING % 'example_code')
        self.assertEqual(len(ws_content), 1)
        wi = ws_content[0]
        CVN._clean_data_learning(wi)
        if u'des1_grado_titulacion' in wi:
            wi[u'des1_grado_titulacion'] = wi[u'des1_grado_titulacion'].upper()
            if wi[u'des1_grado_titulacion'] == u'DOCTOR':
                del wi[u'des1_grado_titulacion']
                if not u'organismo' in wi:
                    wi[u'organismo'] = u'Universidad de La Laguna'
        self.assertEqual(cmp(item, wi), 0)

    @patch.object(CachedWS, 'get', get_cargos_no_f_hasta)
    def test_get_pdf_ull_cargos_no_f_hasta(self):
        self._get_one_cargo_ull()

    @patch.object(CachedWS, 'get', get_cargos_no_departamento)
    def test_get_pdf_ull_cargos_no_departamento(self):
        self._get_one_cargo_ull()

    @patch.object(CachedWS, 'get', get_cargos_no_dedicacion)
    def test_get_pdf_ull_cargos_no_dedicacion(self):
        self._get_one_cargo_ull()

    @patch.object(CachedWS, 'get', get_contratos_no_f_hasta)
    def test_get_pdf_ull_contratos_no_f_hasta(self):
        self._get_one_contrato_ull()

    @patch.object(CachedWS, 'get', get_learning_no_f_expedicion)
    def test_get_pdf_ull_learning_no_f_expedicion(self):
        self._get_one_learning_ull()

    @patch.object(CachedWS, 'get', get_learning_no_organismo)
    def test_get_pdf_ull_learning_no_organismo(self):
        self._get_one_learning_ull()

    @patch.object(CachedWS, 'get', get_learning_doctor_no_organismo)
    def test_get_pdf_ull_learning_doctor_no_organismo(self):
        self._get_one_learning_ull()

    @patch.object(CachedWS, 'get', get_learning_doctor_no_f_expedicion)
    def test_get_pdf_ull_learning_doctor_no_f_expedicion(self):
        self._get_one_learning_ull()

    @patch.object(CachedWS, 'get', get_all)
    def test_get_pdf_ull_filter_by_date(self):
        user = UserFactory.create()
        user.profile.rrhh_code = 'example_code'
        pdf = CVN.get_user_pdf_ull(user=user)
        cvn = CVN(user=user, pdf=pdf)
        cvn.xml_file.open()
        self.assertEqual(len(etree.parse(cvn.xml_file).findall('CvnItem')), 3)

        pdf = CVN.get_user_pdf_ull(user=user)
        cvn = CVN(user=user, pdf=pdf)
        cvn.xml_file.open()
        self.assertEqual(len(etree.parse(cvn.xml_file).findall('CvnItem')), 3)

        pdf = CVN.get_user_pdf_ull(
            user=user, start_date=datetime.date(2012, 1, 1))
        cvn = CVN(user=user, pdf=pdf)
        cvn.xml_file.open()
        self.assertEqual(len(etree.parse(cvn.xml_file).findall('CvnItem')), 1)

        pdf = CVN.get_user_pdf_ull(
            user=user, end_date=datetime.date(2010, 1, 1))
        cvn = CVN(user=user, pdf=pdf)
        cvn.xml_file.open()
        self.assertEqual(len(etree.parse(cvn.xml_file).findall('CvnItem')), 2)

        pdf = CVN.get_user_pdf_ull(
            user=user,
            start_date=datetime.date(2006, 1, 1),
            end_date=datetime.date(2011, 1, 1))
        cvn = CVN(user=user, pdf=pdf)
        cvn.xml_file.open()
        self.assertEqual(len(etree.parse(cvn.xml_file).findall('CvnItem')), 2)

    def test_daterange(self):
        date1 = datetime.date(2001, 1, 1)
        date2 = datetime.date(2001, 12, 31)
        date3 = datetime.date(2002, 1, 1)
        date4 = datetime.date(2003, 1, 1)
        range1 = DateRange(date1, date2)
        range2 = DateRange(date3, date4)
        range3 = DateRange(date2, date4)
        range4 = DateRange(date1, date1)
        range5 = DateRange(date3, date3)
        range6 = DateRange(None, date3)
        range7 = DateRange(date2, None)
        range8 = DateRange(date4, date4)
        range9 = DateRange(date1, date3)
        range10 = DateRange(date2, date4)
        self.assertFalse(range1.intersect(range2))
        self.assertFalse(range3.intersect(range4))
        self.assertTrue(range3.intersect(range5))
        self.assertTrue(range6.intersect(range1))
        self.assertFalse(range6.intersect(range8))
        self.assertTrue(range7.intersect(range8))
        self.assertFalse(range7.intersect(range4))
        self.assertTrue(range9.intersect(range10))

    @patch.object(CachedWS, 'get', get_contratos)
    def test_contrato_dedicacion_ignore_case(self):
        ws_content = CachedWS.get(st.WS_ULL_CONTRATOS % 'example_code')
        w = ws_content[0]
        w[u'dedicacion'] = u'Tiempo completo'
        CVN._cleaned_data_profession(w)
        self.assertTrue(w[u'dedicacion'])

    @classmethod
    def tearDownClass(cls):
        clean()
