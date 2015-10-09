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
from cvn.reports import (UsersReport, DBAreaReport, DBDeptReport, WSAreaReport,
                         WSDeptReport)
from cvn.reports.generators import InformeCSV, ResumenCSV, InformePDF
from cvn.models import (Articulo, Capitulo, Congreso, Convenio, Patente,
                        Proyecto, TesisDoctoral, Libro)
from .mocks.reports import get_area_dept_404
from django.conf import settings as st
from cvn import settings as st_cvn
from statistics.models import Area, Department
import os
from django.core.management import call_command
from bs4 import BeautifulSoup
from core.routers import in_database
from cvn.models import ReportDept, ReportArea
from cvn.reports.shortcuts import get_report_path
from django.test.utils import override_settings

MODEL_BACKEND = 'django.contrib.auth.backends.ModelBackend'


def touch(fname, times=None):
    path = os.path.dirname(fname)
    if not os.path.exists(path):
        os.makedirs(path)
    with open(fname, 'a'):
        os.utime(fname, times)


class CVNTestCase(TestCase):
    multi_db = True

    @classmethod
    def setUpClass(cls):
        init()

    def fill_db(self, range):
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

    def icsv_test(self, output_file, Report, params, year=2013):

        report = Report(InformeCSV, year)
        report.create_report(**params)
        with open(output_file, 'r') as f:
            data = f.read().splitlines()
        self.assertEqual(len(filter(lambda x: x.startswith("ArtName"), data)),
                         Articulo.objects.filter(fecha__year=year).count())
        self.assertEqual(len(filter(lambda x: x.startswith("CapName"), data)),
                         Capitulo.objects.filter(fecha__year=year).count())
        self.assertEqual(len(filter(lambda x: x.startswith("LibName"), data)),
                         Libro.objects.filter(fecha__year=year).count())
        self.assertEqual(
            len(filter(lambda x: x.startswith("ConName"), data)),
            Congreso.objects.filter(fecha_de_inicio__year=year).count()
        )
        self.assertEqual(
            len(filter(lambda x: x.startswith("ConvName"), data)),
            Convenio.objects.filter(fecha_de_inicio__year=year).count()
        )
        self.assertEqual(len(filter(lambda x: x.startswith("PatName"), data)),
                         Patente.objects.filter(fecha__year=year).count())
        self.assertEqual(
            len(filter(lambda x: x.startswith("ProName"), data)),
            Proyecto.objects.filter(fecha_de_inicio__year=year).count()
        )
        self.assertEqual(
            len(filter(lambda x: x.startswith("TesisName"), data)),
            TesisDoctoral.objects.filter(fecha__year=year).count()
        )

    def rcsv_test(self, output_file, Report, n_inv, params, year=2013):
        report = Report(ResumenCSV, year)
        report.create_report(**params)
        report.generator._file.close()
        with open(output_file, 'r') as f:
            data = f.read().splitlines()[1].split("|")[1:]
        self.assertEqual(int(data[0]), n_inv)
        self.assertEqual(int(data[1]), Articulo.objects.filter(fecha__year=year).count())
        self.assertEqual(int(data[2]), Libro.objects.filter(
            fecha__year=year).count())
        self.assertEqual(int(data[3]), Capitulo.objects.filter(
            fecha__year=year).count())
        self.assertEqual(int(data[4]), Congreso.objects.filter(
            fecha_de_inicio__year=year).count())
        self.assertEqual(int(data[5]), Proyecto.objects.filter(
            fecha_de_inicio__year=year).count())
        self.assertEqual(int(data[6]), Convenio.objects.filter(
            fecha_de_inicio__year=year).count())
        self.assertEqual(int(data[7]), TesisDoctoral.objects.filter(
            fecha__year=year).count())
        self.assertEqual(int(data[8]), Patente.objects.filter(
            fecha__year=year).count())

    def pdf_test(self, output_file, Report, params, year=2013):
        report = Report(InformePDF, year)
        report.create_report(**params)
        self.assertTrue(os.path.isfile(output_file))

    @patch.object(CachedWS, 'get', get_area_dept_404)
    @in_database(st.HISTORICAL['2013'], write=True)
    def test_area_icsv(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_ICSV_PATH) +
                       '/area/2013/2013-area-aria.csv')
        self.fill_db(range(1, 5))
        call_command('update_report_data', year='2013')
        self.icsv_test(output_file, DBAreaReport, {"unit": "404"})

    @patch.object(CachedWS, 'get', get_area_dept_404)
    @in_database(st.HISTORICAL['2013'], write=True)
    def test_area_ipdf(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_IPDF_PATH) +
                       '/area/2013/2013-area-aria.pdf')
        self.fill_db(range(1, 5))
        call_command('update_report_data', year='2013')
        self.pdf_test(output_file, DBAreaReport, {"unit": "404"})

    @patch.object(CachedWS, 'get', get_area_dept_404)
    @in_database(st.HISTORICAL['2013'], write=True)
    def test_area_rcsv(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_RCSV_PATH) +
                       '/area/2013/2013-area.csv')
        self.fill_db(range(1, 5))
        call_command('update_report_data', year='2013')
        self.rcsv_test(output_file, DBAreaReport, 5, {"unit": "404"})

    @patch.object(CachedWS, 'get', get_area_dept_404)
    @in_database(st.HISTORICAL['2013'], write=True)
    def test_dept_icsv(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_ICSV_PATH) +
                       '/department/2013/2013-departamento-departamental.csv')
        self.fill_db(range(6, 9))
        call_command('update_report_data', year='2013')
        self.icsv_test(output_file, DBDeptReport, {"unit": "404"})

    @patch.object(CachedWS, 'get', get_area_dept_404)
    @in_database(st.HISTORICAL['2013'], write=True)
    def test_dept_ipdf(self):

        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_IPDF_PATH) +
                       '/department/2013/2013-departamento-departamental.pdf')
        self.fill_db(range(6, 9))
        call_command('update_report_data', year='2013')
        self.pdf_test(output_file, DBDeptReport, {"unit": "404"})

    @patch.object(CachedWS, 'get', get_area_dept_404)
    @in_database(st.HISTORICAL['2013'], write=True)
    def test_dept_rcsv(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_RCSV_PATH) +
                       '/department/2013/2013-department.csv')
        self.fill_db(range(6, 9))
        call_command('update_report_data', year='2013')
        self.rcsv_test(output_file, DBDeptReport, 3, {"unit": "404"})

    @patch.object(CachedWS, 'get', get_area_dept_404)
    @in_database(st.HISTORICAL['2013'], write=True)
    def test_users_rcsv(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_RCSV_PATH) +
                       '/users/2013/2013-users.csv')
        self.fill_db(range(1, 5))
        self.rcsv_test(output_file, UsersReport, 5, {"title": "users"})

    @patch.object(CachedWS, 'get', get_area_dept_404)
    def test_user_ipdf(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_IPDF_PATH) +
                       '/users/2013/2013-informe-users.pdf')
        self.pdf_test(output_file, UsersReport, {"title": "informe-users"})

    @patch.object(CachedWS, 'get', get_area_dept_404)
    def test_user_icsv(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_ICSV_PATH) +
                       '/users/2013/2013-informe-users.csv')
        self.icsv_test(output_file, UsersReport, {"title": "informe-users"})

    @patch.object(CachedWS, 'get', get_area_dept_404)
    def test_wsdept_rcsv(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_RCSV_PATH) +
                       '/department/current/current-department.csv')
        self.fill_db(range(1, 5))
        self.rcsv_test(output_file, WSDeptReport, 3, {"unit": "404"}, 2015)

    @patch.object(CachedWS, 'get', get_area_dept_404)
    def test_wsdept_ipdf(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_IPDF_PATH) +
                       '/department/current/current-departamento-departamental.pdf')
        self.pdf_test(output_file, WSDeptReport, {"unit": "404"}, 2015)

    @patch.object(CachedWS, 'get', get_area_dept_404)
    def test_wsdept_icsv(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_ICSV_PATH) +
                       '/department/current/current-departamento-departamental.csv')
        self.icsv_test(output_file, WSDeptReport, {"unit": "404"}, 2015)

    @patch.object(CachedWS, 'get', get_area_dept_404)
    def test_wsarea_rcsv(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_RCSV_PATH) +
                       '/area/current/current-area.csv')
        self.fill_db(range(1, 5))
        self.rcsv_test(output_file, WSAreaReport, 5, {"unit": "404"}, 2015)

    @patch.object(CachedWS, 'get', get_area_dept_404)
    def test_wsarea_ipdf(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_IPDF_PATH) +
                       '/area/current/current-area-aria.pdf')
        self.pdf_test(output_file, WSAreaReport, {"unit": "404"}, 2015)

    @patch.object(CachedWS, 'get', get_area_dept_404)
    def test_wsarea_icsv(self):
        output_file = (os.path.join(st.MEDIA_ROOT, st_cvn.REPORTS_ICSV_PATH) +
                       '/area/current/current-area-aria.csv')
        self.icsv_test(output_file, WSAreaReport, {"unit": "404"}, 2015)

    @override_settings(AUTHENTICATION_BACKENDS=(MODEL_BACKEND,))
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

    @override_settings(AUTHENTICATION_BACKENDS=(MODEL_BACKEND,))
    def test_user_without_permission_cant_view_admin_reports_link(self):
        u = UserFactory.create_and_login(self.client)
        soup = BeautifulSoup(self.client.get(reverse('cvn')).content, 'lxml')
        reports_link = soup.select('a#admin_reports_link')
        self.assertEqual(len(reports_link), 0)

    @override_settings(AUTHENTICATION_BACKENDS=(MODEL_BACKEND,))
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

    @override_settings(AUTHENTICATION_BACKENDS=(MODEL_BACKEND,))
    def test_user_without_permission_can_view_reports_link(self):
        u = UserFactory.create_and_login(self.client)
        u.profile.rrhh_code = 9354
        u.profile.save()
        soup = BeautifulSoup(self.client.get(reverse('cvn')).content, 'lxml')
        reports_link = soup.select('a#reports_link')
        self.assertEqual(len(reports_link), 1)

    @override_settings(AUTHENTICATION_BACKENDS=(MODEL_BACKEND,))
    def test_user_without_permission_cant_view_admin_reports(self):
        u = UserFactory.create_and_login(self.client)
        response = self.client.get(reverse('admin_reports'))
        self.assertEqual(response.status_code, 404)

    @override_settings(AUTHENTICATION_BACKENDS=(MODEL_BACKEND,))
    def test_user_with_permission_can_view_admin_reports(self):
        u = UserFactory.create_and_login(self.client)
        u.user_permissions.add(Permission.objects.get(
            codename='read_cvn_reports'))
        u.user_permissions.add(Permission.objects.get(
            codename='read_admin_menu'))
        u.save()
        response = self.client.get(reverse('admin_reports'))
        self.assertEqual(response.status_code, 200)

    @override_settings(AUTHENTICATION_BACKENDS=(MODEL_BACKEND,))
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

    @override_settings(AUTHENTICATION_BACKENDS=(MODEL_BACKEND,))
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

    def _create_dept_and_area_fake(self, year, code, report_type):
        with in_database(st.HISTORICAL[year], write=True):
            ReportDept.objects.create(code=code, name='Departamento 1')
            ReportArea.objects.create(code=code, name='Area 1')
        dept_path = get_report_path(unit_type='dept', report_type=report_type,
                                    year=year, code=code, check_file=False)
        area_path = get_report_path(unit_type='area', report_type=report_type,
                                    year=year, code=code, check_file=False)
        touch(dept_path)
        touch(area_path)

    @override_settings(AUTHENTICATION_BACKENDS=(MODEL_BACKEND,))
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
        self._create_dept_and_area_fake('2014', 4987, 'rcsv')
        response = self.client.get(reverse('download_report', kwargs={
            'type': 'rcsv', 'year': '2014', 'unit_type': 'dept'}))
        self.assertEqual(response.status_code, 200)

    @override_settings(AUTHENTICATION_BACKENDS=(MODEL_BACKEND,))
    def test_user_without_permission_cant_download_rcsv(self):
        u = UserFactory.create_and_login(self.client)
        session = self.client.session  # session has to be put in a variable
        session['dept_code'] = 4987
        session['area_code'] = 4987
        session.save()
        self._create_dept_and_area_fake('2014', 4987, 'rcsv')
        response = self.client.get(reverse('download_report', kwargs={
            'type': 'rcsv', 'year': '2014', 'unit_type': 'dept'}))
        self.assertEqual(response.status_code, 404)

    @override_settings(AUTHENTICATION_BACKENDS=(MODEL_BACKEND,))
    def test_user_with_permission_can_download_icsv(self):
        u = UserFactory.create_and_login(self.client)
        u.user_permissions.add(Permission.objects.get(
            codename='read_cvn_reports'))
        u.user_permissions.add(Permission.objects.get(
            codename='read_admin_menu'))
        u.save()
        session = self.client.session  # session has to be put in a variable
        session['dept_code'] = 4988
        session['area_code'] = 4988
        session.save()
        self._create_dept_and_area_fake('2014', 4987, 'icsv')
        response = self.client.get(reverse('download_report', kwargs={
            'type': 'icsv', 'year': '2014', 'unit_type': 'dept',
            'code': '4987'}))
        self.assertEqual(response.status_code, 200)

    @override_settings(AUTHENTICATION_BACKENDS=(MODEL_BACKEND,))
    def test_user_without_permission_cant_download_icsv(self):
        u = UserFactory.create_and_login(self.client)
        session = self.client.session  # session has to be put in a variable
        session['dept_code'] = 4988
        session['area_code'] = 4988
        session.save()
        self._create_dept_and_area_fake('2014', 4987, 'icsv')
        response = self.client.get(reverse('download_report', kwargs={
            'type': 'icsv', 'year': '2014', 'unit_type': 'dept',
            'code': '4987'}))
        self.assertEqual(response.status_code, 404)

    @override_settings(AUTHENTICATION_BACKENDS=(MODEL_BACKEND,))
    def test_user_without_permission_can_download_his_icsv(self):
        u = UserFactory.create_and_login(self.client)
        session = self.client.session  # session has to be put in a variable
        session['dept_code'] = 4987
        session['area_code'] = 4987
        session.save()
        self._create_dept_and_area_fake('2014', 4987, 'icsv')
        response = self.client.get(reverse('download_report', kwargs={
            'type': 'icsv', 'year': '2014', 'unit_type': 'dept',
            'code': '4987'}))
        self.assertEqual(response.status_code, 200)

    @override_settings(AUTHENTICATION_BACKENDS=(MODEL_BACKEND,))
    def test_user_with_permission_can_download_ipdf(self):
        u = UserFactory.create_and_login(self.client)
        u.user_permissions.add(Permission.objects.get(
            codename='read_cvn_reports'))
        u.user_permissions.add(Permission.objects.get(
            codename='read_admin_menu'))
        u.save()
        session = self.client.session  # session has to be put in a variable
        session['dept_code'] = 4988
        session['area_code'] = 4988
        session.save()
        self._create_dept_and_area_fake('2014', 4987, 'ipdf')
        response = self.client.get(reverse('download_report', kwargs={
            'type': 'ipdf', 'year': '2014', 'unit_type': 'dept',
            'code': '4987'}))
        self.assertEqual(response.status_code, 200)

    @override_settings(AUTHENTICATION_BACKENDS=(MODEL_BACKEND,))
    def test_user_without_permission_cant_download_ipdf(self):
        u = UserFactory.create_and_login(self.client)
        session = self.client.session  # session has to be put in a variable
        session['dept_code'] = 4988
        session['area_code'] = 4988
        session.save()
        self._create_dept_and_area_fake('2014', 4987, 'ipdf')
        response = self.client.get(reverse('download_report', kwargs={
            'type': 'ipdf', 'year': '2014', 'unit_type': 'dept',
            'code': '4987'}))
        self.assertEqual(response.status_code, 404)

    @override_settings(AUTHENTICATION_BACKENDS=(MODEL_BACKEND,))
    def test_user_without_permission_can_download_his_ipdf(self):
        u = UserFactory.create_and_login(self.client)
        session = self.client.session  # session has to be put in a variable
        session['dept_code'] = 4987
        session['area_code'] = 4987
        session.save()
        self._create_dept_and_area_fake('2014', 4987, 'ipdf')
        response = self.client.get(reverse('download_report', kwargs={
            'type': 'ipdf', 'year': '2014', 'unit_type': 'dept',
            'code': '4987'}))
        self.assertEqual(response.status_code, 200)

    @classmethod
    def tearDownClass(cls):
        clean()
