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
from os.path import join as os_path_join
from django.test import TestCase
from django.conf import settings as st
from cvn import settings as st_cvn
from cvn.models import CVN, OldCvnPdf
from cvn.helpers import get_cvn_path as get_cvn_helpers_path
from cvn.helpers import get_old_cvn_path
from core.tests.helpers import init, clean
from core.tests.factories import UserFactory
from utils import get_cvn_path
from core.admin_advanced import change_dni_cvn, change_dni_cvn_old


class CVNTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        init()

    def setUp(self):
        self.xml_ull = open(os.path.join(st_cvn.FILE_TEST_ROOT,
                            'xml/CVN-ULL.xml'))
        self.xml_empty = open(os.path.join(st_cvn.FILE_TEST_ROOT,
                              'xml/empty.xml'))
        self.xml_test = open(os.path.join(st_cvn.FILE_TEST_ROOT,
                             'xml/CVN-Test.xml'))

    def test_on_insert_cvn_old_pdf_is_moved(self):
        user = UserFactory.create()
        cvn = CVN(user=user, pdf_path=get_cvn_path('CVN-Test'))
        cvn.save()
        filename = cvn.cvn_file.name.split('/')[-1].replace(
            u'.pdf', u'-' + str(
                cvn.uploaded_at.strftime('%Y-%m-%d-%Hh%Mm%Ss')
            ) + u'.pdf')
        old_cvn_path = os.path.join(
            '/'.join(cvn.cvn_file.path.split('/')[:-1]), 'old', filename)
        CVN(user=user, pdf_path=get_cvn_path('CVN-Test'))
        self.assertTrue(os.path.isfile(old_cvn_path))
        self.assertEqual(OldCvnPdf.objects.filter(
            user_profile=user.profile, uploaded_at=cvn.uploaded_at).count(), 1)

    def test_valid_identity_nif_without_letter(self):
        user = UserFactory.create()
        user.profile.documento = '11111111H'
        user.profile.save()
        cvn = CVN(user=user, pdf_path=get_cvn_path('CVN-NIF-sin_letra'))
        self.assertNotEqual(cvn.status, st_cvn.CVNStatus.INVALID_IDENTITY)

    def test_update_from_pdf(self):
        us = UserFactory.create()
        cvn = CVN(user=us)
        pdf_file = file(get_cvn_path('CVN-Test'))
        cvn.update_from_pdf(pdf_file.read())
        self.assertTrue(cvn.xml_file and cvn.cvn_file)

    def test_update_from_xml(self):
        us = UserFactory.create()
        cvn = CVN(user=us)
        xml_file = file(os.path.join(
            st_cvn.FILE_TEST_ROOT, 'xml/CVN-Test.xml'))
        cvn.update_from_xml(xml_file.read())
        self.assertTrue(cvn.xml_file and cvn.cvn_file)

    @classmethod
    def tearDownClass(cls):
        clean()

    def test_dni_change(self):
        #LATEST CVN TEST
        user = UserFactory.create()
        cvn = CVN(user=user, pdf_path=get_cvn_path('CVN-Test'))
        cvn.save()
        user.profile.documento = '88888888O'
        user.profile.save()
        pdf_rel_path = get_cvn_helpers_path(cvn, u'test.pdf')
        pdf_path = os_path_join(st.MEDIA_ROOT, pdf_rel_path)
        xml_rel_path = get_cvn_helpers_path(cvn, u'test.xml')
        xml_path = os_path_join(st.MEDIA_ROOT, xml_rel_path)
        change_dni_cvn(user.profile)
        self.assertEqual(cvn.cvn_file.path,pdf_path)
        self.assertEqual(cvn.xml_file.path,xml_path)

        #OLD CVN TEST
        user_old = UserFactory.create()
        cvn2 = CVN(user=user_old, pdf_path=get_cvn_path('CVN-Test'))
        cvn2.save()
        CVN(user=user_old, pdf_path=get_cvn_path('CVN-Test'))
        user_old.profile.documento = '7777777D'
        user_old.save()
        filename_old = 'CVN-%s-%s.pdf'%(user_old.profile.documento, user_old.profile.oldcvnpdf_set.all()[0].uploaded_at.strftime('%Y-%m-%d-%Hh%Mm%Ss'))
        pdf_path_old = get_old_cvn_path(cvn2, filename_old)
        path_old = os_path_join(st.MEDIA_ROOT, pdf_path_old)
        change_dni_cvn_old(user_old.profile)
        cvn_old =user_old.profile.oldcvnpdf_set.all()[0]
        self.assertEqual(cvn_old.cvn_file.path, path_old)