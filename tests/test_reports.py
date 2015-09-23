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

import datetime
from random import randint
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Permission
from mock import patch
from core.ws_utils import CachedWS
from core.tests.helpers import init, clean
from core.tests.factories import UserFactory
from cvn.reports import UsersReport, AreaReport, DeptReport
from cvn.reports.generators import InformeCSV, ResumenCSV, InformePDF
from cvn.models import (Articulo, Capitulo, Congreso, Convenio, Patente,
                        Proyecto, TesisDoctoral, Libro)
from .mocks.reports import get_dept_404, get_area_404
from django.conf import settings as st
from cvn import settings as st_cvn
from statistics.models import Area, Department
import os
from bs4 import BeautifulSoup


class CVNTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        init()

    def icsv_test(self, output_file, Report, range, params):
        for i in range:
            u = UserFactory.create()
            u.profile.rrhh_code = i
            u.profile.save()

            a = Articulo(titulo="ArtName" + str(i),
                         fecha=datetime.date(randint(2012, 2014), 1, 1))
            a.save()
            a.user_profile.add(u.profile)

            a = Capitulo(titulo="CapName" + str(i),
                         fecha=datetime.date(randint(2012, 2014), 1, 1))
            a.save()
            a.user_profile.add(u.profile)

            a = Libro(titulo="LibName" + str(i),
                      fecha=datetime.date(randint(2012, 2014), 1, 1))
            a.save()
            a.user_profile.add(u.profile)

            a = Congreso(
                titulo="ConName" + str(i),
                fecha_de_inicio=datetime.date(randint(2012, 2014), 1, 1)
            )
            a.save()
            a.user_profile.add(u.profile)

            a = Convenio(
                titulo="ConvName" + str(i),
                fecha_de_inicio=datetime.date(randint(2012, 2014), 1, 1)
            )
            a.save()
            a.user_profile.add(u.profile)

            a = Patente(titulo="PatName" + str(i),
                        fecha=datetime.date(randint(2012, 2014), 1, 1))
            a.save()
            a.user_profile.add(u.profile)

            a = Proyecto(
                titulo="ProName" + str(i),
                fecha_de_inicio=datetime.date(randint(2012, 2014), 1, 1)
            )
            a.save()
            a.user_profile.add(u.profile)

            a = TesisDoctoral(titulo="TesisName" + str(i),
                              fecha=datetime.date(randint(2012, 2014), 1, 1))
            a.save()
            a.user_profile.add(u.profile)

        report = Report(InformeCSV, 2013)
        report.create_report(**params)
        with open(output_file, 'r') as f:
            data = f.read().splitlines()
        self.assertEqual(len(filter(lambda x: x.startswith("ArtName"), data)),
                         Articulo.objects.filter(fecha__year='2013').count())
        self.assertEqual(len(filter(lambda x: x.startswith("CapName"), data)),
                         Capitulo.objects.filter(fecha__year='2013').count())
        self.assertEqual(len(filter(lambda x: x.startswith("LibName"), data)),
                         Libro.objects.filter(fecha__year='2013').count())
        self.assertEqual(
            len(filter(lambda x: x.startswith("ConName"), data)),
            Congreso.objects.filter(fecha_de_inicio__year='2013').count()
        )
        self.assertEqual(
            len(filter(lambda x: x.startswith("ConvName"), data)),
            Convenio.objects.filter(fecha_de_inicio__year='2013').count()
        )
        self.assertEqual(len(filter(lambda x: x.startswith("PatName"), data)),
                         Patente.objects.filter(fecha__year='2013').count())
        self.assertEqual(
            len(filter(lambda x: x.startswith("ProName"), data)),
            Proyecto.objects.filter(fecha_de_inicio__year='2013').count()
        )
        self.assertEqual(
            len(filter(lambda x: x.startswith("TesisName"), data)),
            TesisDoctoral.objects.filter(fecha__year='2013').count()
        )

    def rcsv_test(self, output_file, report, range, n_inv, params):
        for i in range:
            u = UserFactory.create()
            u.profile.rrhh_code = i
            u.profile.save()

            a = Articulo(titulo="ArtName" + str(i),
                         fecha=datetime.date(randint(2012, 2014), 1, 1))
            a.save()
            a.user_profile.add(u.profile)

            a = Capitulo(titulo="CapName" + str(i),
                         fecha=datetime.date(randint(2012, 2014), 1, 1))
            a.save()
            a.user_profile.add(u.profile)

            a = Congreso(
                titulo="ConName" + str(i),
                fecha_de_inicio=datetime.date(randint(2012, 2014), 1, 1)
            )
            a.save()
            a.user_profile.add(u.profile)

            a = Convenio(
                titulo="ConvName" + str(i),
                fecha_de_inicio=datetime.date(randint(2012, 2014), 1, 1)
            )
            a.save()
            a.user_profile.add(u.profile)

            a = Patente(titulo="PatName" + str(i),
                        fecha=datetime.date(randint(2012, 2014), 1, 1))
            a.save()
            a.user_profile.add(u.profile)

            a = Proyecto(
                titulo="ProName" + str(i),
                fecha_de_inicio=datetime.date(randint(2012, 2014), 1, 1)
            )
            a.save()
            a.user_profile.add(u.profile)

            a = TesisDoctoral(titulo="TesisName" + str(i),
                              fecha=datetime.date(randint(2012, 2014), 1, 1))
            a.save()
            a.user_profile.add(u.profile)

        report_ = report(ResumenCSV, 2013)
        report_.create_report(**params)
        report_.generator._file.close()
        with open(output_file, 'r') as f:
            data = f.read().splitlines()[1].split("|")[1:]
        self.assertEqual(int(data[0]), n_inv)
        self.assertEqual(int(data[1]), Articulo.objects.filter(
            fecha__year='2013').count())
        self.assertEqual(int(data[2]), Libro.objects.filter(
            fecha__year='2013').count())
        self.assertEqual(int(data[3]), Capitulo.objects.filter(
            fecha__year='2013').count())
        self.assertEqual(int(data[4]), Congreso.objects.filter(
            fecha_de_inicio__year='2013').count())
        self.assertEqual(int(data[5]), Proyecto.objects.filter(
            fecha_de_inicio__year='2013').count())
        self.assertEqual(int(data[6]), Convenio.objects.filter(
            fecha_de_inicio__year='2013').count())
        self.assertEqual(int(data[7]), TesisDoctoral.objects.filter(
            fecha__year='2013').count())
        self.assertEqual(int(data[8]), Patente.objects.filter(
            fecha__year='2013').count())

    def pdf_test(self, output_file, Report, range, params):
        for i in range:
            u = UserFactory.create()
            u.profile.rrhh_code = i
            u.profile.save()

            a = Articulo(titulo="ArtName" + str(i),
                         fecha=datetime.date(randint(2012, 2014), 1, 1))
            a.save()
            a.user_profile.add(u.profile)

            a = Capitulo(titulo="CapName" + str(i),
                         fecha=datetime.date(randint(2012, 2014), 1, 1))
            a.save()
            a.user_profile.add(u.profile)

            a = Congreso(
                titulo="ConName" + str(i),
                fecha_de_inicio=datetime.date(randint(2012, 2014), 1, 1)
            )
            a.save()
            a.user_profile.add(u.profile)

            a = Convenio(
                titulo="ConvName" + str(i),
                fecha_de_inicio=datetime.date(randint(2012, 2014), 1, 1)
            )
            a.save()
            a.user_profile.add(u.profile)

            a = Patente(titulo="PatName" + str(i),
                        fecha=datetime.date(randint(2012, 2014), 1, 1))
            a.save()
            a.user_profile.add(u.profile)

            a = Proyecto(
                titulo="ProName" + str(i),
                fecha_de_inicio=datetime.date(randint(2012, 2014), 1, 1)
            )
            a.save()
            a.user_profile.add(u.profile)

            a = TesisDoctoral(titulo="TesisName" + str(i),
                              fecha=datetime.date(randint(2012, 2014), 1, 1))
            a.save()
            a.user_profile.add(u.profile)

        report = Report(InformePDF, 2013)
        report.create_report(**params)
        self.assertTrue(os.path.isfile(output_file))

    @patch.object(CachedWS, 'get', get_area_404)
    def test_area_icsv(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_ICSV_PATH)
                       + '/area/2013/2013-area-aria.csv')
        self.icsv_test(output_file, AreaReport, range(1, 5), {"unit": "404"})

    @patch.object(CachedWS, 'get', get_area_404)
    def test_area_ipdf(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_IPDF_PATH)
                       + '/area/2013/2013-area-aria.pdf')
        self.pdf_test(output_file, AreaReport, range(1, 5), {"unit": "404"})

    @patch.object(CachedWS, 'get', get_area_404)
    def test_area_rcsv(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_RCSV_PATH)
                       + '/area/2013/2013-area.csv')
        self.rcsv_test(output_file, AreaReport, range(1, 5), 4, {"unit": "404"})

    @patch.object(CachedWS, 'get', get_dept_404)
    def test_dept_icsv(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_ICSV_PATH)
                       + '/department/2013/2013-departamento-departamental.csv')
        self.icsv_test(output_file, DeptReport, range(5, 8), {"unit": "404"})

    @patch.object(CachedWS, 'get', get_dept_404)
    def test_dept_ipdf(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_IPDF_PATH)
                       + '/department/2013/2013-departamento-departamental.pdf')
        self.pdf_test(output_file, DeptReport, range(5, 8), {"unit": "404"})

    @patch.object(CachedWS, 'get', get_dept_404)
    def test_dept_rcsv(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_RCSV_PATH)
                       + '/department/2013/2013-department.csv')
        self.rcsv_test(output_file, DeptReport, range(5, 8), 3, {"unit": "404"})

    @patch.object(CachedWS, 'get', get_dept_404)
    def test_users_rcsv(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_RCSV_PATH)
                       + '/users/2013/2013-users.csv')
        self.rcsv_test(output_file, UsersReport, range(1, 5), 5,
                       {"title": "users"})

    @patch.object(CachedWS, 'get', get_dept_404)
    def test_user_ipdf(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_IPDF_PATH)
                       + '/users/2013/2013-informe-users.pdf')
        self.pdf_test(output_file, UsersReport, range(5, 8),
                      {"title": "informe-users"})

    @patch.object(CachedWS, 'get', get_dept_404)
    def test_user_icsv(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_ICSV_PATH)
                       + '/users/2013/2013-informe-users.csv')
        self.icsv_test(output_file, UsersReport, range(5, 8),
                       {"title": "informe-users"})

    def test_user_with_permission_can_view_admin_reports_link(self):
        u = UserFactory.create_and_login(self.client)
        u.user_permissions.add(Permission.objects.get(
            codename='read_cvn_reports'))
        u.user_permissions.add(Permission.objects.get(
            codename='read_admin_menu'))
        u.save()
        soup = BeautifulSoup(self.client.get(reverse('cvn')).content, 'lxml')
        reports_link = soup.select('a#admin_reports_link')
        self.assertEqual(len(reports_link), 1)
        st.AUTHENTICATION_BACKENDS = ('core.backends.CASBackend',)

    def test_user_without_permission_cant_view_admin_reports_link(self):
        u = UserFactory.create_and_login(self.client)
        soup = BeautifulSoup(self.client.get(reverse('cvn')).content, 'lxml')
        reports_link = soup.select('a#admin_reports_link')
        self.assertEqual(len(reports_link), 0)
        st.AUTHENTICATION_BACKENDS = ('core.backends.CASBackend',)

    def test_user_with_permission_cant_view_reports_link(self):
        u = UserFactory.create_and_login(self.client)
        u.profile.rrhh_code = 9354
        u.profile.save()
        u.user_permissions.add(Permission.objects.get(
            codename='read_cvn_reports'))
        u.user_permissions.add(Permission.objects.get(
            codename='read_admin_menu'))
        u.save()
        soup = BeautifulSoup(self.client.get(reverse('cvn')).content, 'lxml')
        reports_link = soup.select('a#reports_link')
        self.assertEqual(len(reports_link), 0)
        st.AUTHENTICATION_BACKENDS = ('core.backends.CASBackend',)

    def test_user_without_permission_can_view_reports_link(self):
        u = UserFactory.create_and_login(self.client)
        u.profile.rrhh_code = 9354
        u.profile.save()
        soup = BeautifulSoup(self.client.get(reverse('cvn')).content, 'lxml')
        reports_link = soup.select('a#reports_link')
        self.assertEqual(len(reports_link), 1)
        st.AUTHENTICATION_BACKENDS = ('core.backends.CASBackend',)

    def test_user_without_permission_cant_view_admin_reports(self):
        u = UserFactory.create_and_login(self.client)
        response = self.client.get(reverse('admin_reports'))
        self.assertEqual(response.status_code, 404)
        st.AUTHENTICATION_BACKENDS = ('core.backends.CASBackend',)

    def test_user_with_permission_can_view_admin_reports(self):
        u = UserFactory.create_and_login(self.client)
        u.user_permissions.add(Permission.objects.get(
            codename='read_cvn_reports'))
        u.user_permissions.add(Permission.objects.get(
            codename='read_admin_menu'))
        u.save()
        response = self.client.get(reverse('admin_reports'))
        self.assertEqual(response.status_code, 200)
        st.AUTHENTICATION_BACKENDS = ('core.backends.CASBackend',)

    def test_user_without_permission_can_view_reports(self):
        u = UserFactory.create_and_login(self.client)
        Department.objects.create(
            code=4987, name="dept1", members=[], commit=True)
        Area.objects.create(code=4987, name="area1", members=[], commit=True)
        session = self.client.session  # session has to be put in a variable
        session['dept_code'] = 4987
        session['area_code'] = 4987
        session.save()
        response = self.client.get(reverse('reports'))
        self.assertEqual(response.status_code, 200)
        st.AUTHENTICATION_BACKENDS = ('core.backends.CASBackend',)

    def test_user_with_permission_can_view_reports(self):
        u = UserFactory.create_and_login(self.client)
        u.user_permissions.add(Permission.objects.get(
            codename='read_cvn_reports'))
        u.user_permissions.add(Permission.objects.get(
            codename='read_admin_menu'))
        u.save()
        Department.objects.create(
            code=4987, name="dept1", members=[], commit=True)
        Area.objects.create(code=4987, name="area1", members=[], commit=True)
        session = self.client.session  # session has to be put in a variable
        session['dept_code'] = 4987
        session['area_code'] = 4987
        session.save()
        response = self.client.get(reverse('reports'))
        self.assertEqual(response.status_code, 200)
        st.AUTHENTICATION_BACKENDS = ('core.backends.CASBackend',)

    def test_user_with_permission_can_download_rcsv(self):
        u = UserFactory.create_and_login(self.client)
        u.user_permissions.add(Permission.objects.get(
            codename='read_cvn_reports'))
        u.user_permissions.add(Permission.objects.get(
            codename='read_admin_menu'))
        u.save()
        session = self.client.session  # session has to be put in a variable
        session['dept_code'] = 4987
        session['area_code'] = 4987
        session.save()
        response = self.client.get(reverse('download_report', kwargs={
            'type': 'rcsv', 'year': '2015', 'unit_type': 'dept'}))
        self.assertEqual(response.status_code, 200)
        st.AUTHENTICATION_BACKENDS = ('core.backends.CASBackend',)

    def test_user_without_permission_cant_download_rcsv(self):
        u = UserFactory.create_and_login(self.client)
        session = self.client.session  # session has to be put in a variable
        session['dept_code'] = 4987
        session['area_code'] = 4987
        session.save()
        response = self.client.get(reverse('download_report', kwargs={
            'type': 'rcsv', 'year': '2015', 'unit_type': 'dept'}))
        self.assertEqual(response.status_code, 404)
        st.AUTHENTICATION_BACKENDS = ('core.backends.CASBackend',)

    @classmethod
    def tearDownClass(cls):
        clean()
