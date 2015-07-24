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

from .helpers import get_cvn_path, get_old_cvn_path, DateRange
from core.models import UserProfile
from core.ws_utils import CachedWS as ws
from cvn import settings as st_cvn
from django.conf import settings as st
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.utils.translation import ugettext_lazy as _
from lxml import etree
from managers import CongresoManager, ScientificExpManager, CvnItemManager
from parsers.read_helpers import parse_date, parse_nif, parse_cvnitem_to_class
from parsers.write import CvnXmlWriter
from constance import config

import datetime
import fecyt
import logging

logger = logging.getLogger('cvn')


class CVN(models.Model):

    cvn_file = models.FileField(_(u'PDF'), upload_to=get_cvn_path)

    xml_file = models.FileField(_(u'XML'), upload_to=get_cvn_path)

    fecha = models.DateField(_("Date of CVN"))

    created_at = models.DateTimeField(_("Created"), auto_now_add=True)

    updated_at = models.DateTimeField(_("Updated"), auto_now=True)

    uploaded_at = models.DateTimeField(
        _("Uploaded PDF"), default=datetime.datetime(2014, 10, 18))

    user_profile = models.OneToOneField(UserProfile)

    status = models.IntegerField(_("Status"), choices=st_cvn.CVN_STATUS)

    is_inserted = models.BooleanField(_("Inserted"), default=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        pdf_path = kwargs.pop('pdf_path', None)
        pdf = kwargs.pop('pdf', None)
        super(CVN, self).__init__(*args, **kwargs)
        if user:
            self.user_profile = user.profile
        if pdf_path:
            pdf_file = open(pdf_path)
            pdf = pdf_file.read()
        if pdf and user:
            self.update_from_pdf(pdf, commit=False)

    def update_from_pdf(self, pdf, commit=True):
        name = 'CVN-' + self.user_profile.documento
        (xml, error) = fecyt.pdf2xml(pdf, name)
        if not error:
            CVN.remove_cvn_by_userprofile(self.user_profile)
            self.cvn_file = SimpleUploadedFile(name, pdf,
                                               content_type="application/pdf")
            self.initialize_fields(xml, commit)

    def update_from_xml(self, xml, commit=True):
        pdf = fecyt.xml2pdf(xml)
        if pdf:
            self.update_from_pdf(pdf, commit)

    def initialize_fields(self, xml, commit=True):
        # Warning: The filename is ignored by your extension is needed
        self.xml_file.save(u'fake-filename.xml', ContentFile(xml), save=False)
        tree_xml = etree.XML(xml)
        self.fecha = parse_date(tree_xml.find('Version/VersionID/Date'))
        self.is_inserted = False
        self.uploaded_at = datetime.datetime.now()
        self.update_status(commit)
        self.xml_file.close()
        if commit:
            self.save()

    def update_status(self, commit=True):
        status = self.status
        if self.fecha <= config.EXPIRY_DATE:
            self.status = st_cvn.CVNStatus.EXPIRED
        elif not self._is_valid_identity():
            self.status = st_cvn.CVNStatus.INVALID_IDENTITY
        else:
            self.status = st_cvn.CVNStatus.UPDATED
        if self.status != status and commit:
            self.save()

    def _is_valid_identity(self):
        try:
            if self.xml_file.closed:
                self.xml_file.open()
        except IOError:
            return False
        xml_tree = etree.parse(self.xml_file)
        self.xml_file.seek(0)
        nif = parse_nif(xml_tree)
        self.xml_file.close()
        for character in [' ', '-']:
            if character in nif:
                nif = nif.replace(character, '')
        if nif.upper() == self.user_profile.documento.upper():
            return True
        # NIF/NIE without final letter
        if len(nif) == 8 and nif == self.user_profile.documento[:-1]:
            return True
        return False

    @classmethod
    def get_user_pdf_ull(cls, user, start_date=None, end_date=None):
        if user.profile.rrhh_code is None:
            return None
        parser = CvnXmlWriter(user=user)

        learning = cls._insert_learning(user, parser, start_date, end_date)

        cargos = cls._insert_profession(
            st.WS_ULL_CARGOS, user, parser, start_date, end_date)

        contratos = cls._insert_profession(
            st.WS_ULL_CONTRATOS, user, parser, start_date, end_date)

        docencia = cls._insert_teaching(user, parser, start_date, end_date)

        if not learning and not cargos and not contratos and not docencia:
            return None

        xml = parser.tostring()
        return fecyt.xml2pdf(xml)

    @classmethod
    def _insert_learning(cls, user, parser, start_date, end_date):
        items = ws.get(url=st.WS_ULL_LEARNING % user.profile.rrhh_code,
                       use_redis=True)
        counter = 0
        if items is None:
            return counter
        for item in items:
            values = item.copy()
            cls._clean_data_learning(values)
            item_date_range = DateRange(
                values[u'f_expedicion'], values[u'f_expedicion'])
            if not item_date_range.intersect(DateRange(
                    start_date, end_date)):
                continue
            if (u'des1_grado_titulacion' in item
                    and item[u'des1_grado_titulacion'].upper() == u'DOCTOR'):
                del values[u'des1_grado_titulacion']
                parser.add_learning_phd(**values)
            else:
                parser.add_learning(**values)
            counter += 1
        return counter

    @staticmethod
    def _clean_data_learning(item):
        if u'f_expedicion' in item and item[u'f_expedicion'] is not None:
            item[u'f_expedicion'] = datetime.datetime.strptime(
                item[u'f_expedicion'], "%d-%m-%Y").date()
        else:
            item[u'f_expedicion'] = None

    @classmethod
    def _insert_profession(cls, ws_url, user, parser, start_date, end_date):
        items = ws.get(url=ws_url % user.profile.rrhh_code, use_redis=True)
        counter = 0
        if items is None:
            return counter
        for item in items:
            values = item.copy()
            cls._cleaned_data_profession(values)
            if u'f_toma_posesion' in item:
                initial_date = values[u'f_toma_posesion']
            else:
                initial_date = values[u'f_desde']
            item_date_range = DateRange(initial_date, values[u'f_hasta'])
            if not item_date_range.intersect(DateRange(
                    start_date, end_date)):
                continue
            parser.add_profession(**values)
            counter += 1
        return counter

    @staticmethod
    def _cleaned_data_profession(item):
        if u'f_toma_posesion' in item and item[u'f_toma_posesion'] is not None:
            item[u'f_toma_posesion'] = datetime.datetime.strptime(
                item[u'f_toma_posesion'], "%d-%m-%Y").date()

        if u'f_desde' in item and item[u'f_desde'] is not None:
            item[u'f_desde'] = datetime.datetime.strptime(
                item[u'f_desde'], "%d-%m-%Y").date()

        if u'f_hasta' in item and item[u'f_hasta'] is not None:
            item[u'f_hasta'] = datetime.datetime.strptime(
                item[u'f_hasta'], "%d-%m-%Y").date()
        else:
            item[u'f_hasta'] = None

        if u'dedicacion' in item:
            dedicacion = item[u'dedicacion'].upper()
            item[u'dedicacion'] = dedicacion == u'TIEMPO COMPLETO'

    @classmethod
    def _insert_teaching(cls, user, parser, start_date, end_date):
        items = ws.get(url=st.WS_ULL_TEACHING % user.profile.rrhh_code,
                       use_redis=True)
        counter = 0
        if items is None:
            return counter
        for item in items:
            values = item.copy()
            date = datetime.date(int(values[u'curso_inicio']), 1, 1)
            item_date_range = DateRange(date, date)
            if not item_date_range.intersect(DateRange(start_date, end_date)):
                continue
            parser.add_teaching(**values)
            counter += 1
        return counter

    @staticmethod
    def create(user, xml=None):
        if not xml:
            parser = CvnXmlWriter(user=user)
            xml = parser.tostring()
        pdf = fecyt.xml2pdf(xml)
        if pdf is None:
            return None
        cvn = CVN(user=user, pdf=pdf)
        cvn.save()
        return cvn

    @classmethod
    def remove_cvn_by_userprofile(cls, user_profile):
        try:
            cvn_old = cls.objects.get(user_profile=user_profile)
            cvn_old.remove()
        except ObjectDoesNotExist:
            pass

    def remove(self):
        # Removes data related to CVN that is not on the CVN class.
        self._backup_pdf()
        try:
            if self.cvn_file:
                self.cvn_file.delete(False)  # Remove PDF file
        except IOError as e:
            logger.error(str(e))
        try:
            if self.xml_file:
                self.xml_file.delete(False)  # Remove XML file
        except IOError as e:
            logger.error(str(e))

    def _backup_pdf(self):
        filename = self.cvn_file.name.split('/')[-1].replace(
            u'.pdf', u'-' + str(
                self.uploaded_at.strftime('%Y-%m-%d-%Hh%Mm%Ss')
            ) + u'.pdf')
        try:
            old_cvn_file = SimpleUploadedFile(
                filename, self.cvn_file.read(), content_type="application/pdf")
        except IOError as e:
            logger.error(e.message)
        else:
            cvn_old = OldCvnPdf(
                user_profile=self.user_profile, cvn_file=old_cvn_file,
                uploaded_at=self.uploaded_at)
            cvn_old.save()

    def remove_producciones(self):
        Articulo.remove_by_userprofile(self.user_profile)
        Libro.remove_by_userprofile(self.user_profile)
        Capitulo.remove_by_userprofile(self.user_profile)
        Congreso.remove_by_userprofile(self.user_profile)
        Proyecto.remove_by_userprofile(self.user_profile)
        Convenio.remove_by_userprofile(self.user_profile)
        TesisDoctoral.remove_by_userprofile(self.user_profile)
        Patente.remove_by_userprofile(self.user_profile)

    def insert_xml(self):
        try:
            if self.xml_file.closed:
                self.xml_file.open()
            self.xml_file.seek(0)
            cvn_items = etree.parse(self.xml_file).findall('CvnItem')
            self._parse_cvn_items(cvn_items)
            self.is_inserted = True
            self.save()
        except IOError:
            if self.xml_file:
                logger.error((u'No existe el fichero' + u' %s') % (
                    self.xml_file.name))
            else:
                logger.warning(u'Se requiere de un fichero CVN-XML')

    def _parse_cvn_items(self, cvn_items):
        for cvnitem in cvn_items:
            produccion = parse_cvnitem_to_class(cvnitem)
            if produccion is None:
                continue
            produccion.objects.create(cvnitem, self.user_profile)

    def __unicode__(self):
        return '%s ' % self.cvn_file.name.split('/')[-1]

    class Meta:
        verbose_name_plural = _("Normalized Curriculum Vitae")
        ordering = ['-uploaded_at', '-updated_at']


class Publicacion(models.Model):
    """
        https://cvn.fecyt.es/editor/cvn.html?locale=spa#ACTIVIDAD_CIENTIFICA
    """

    objects = CvnItemManager()

    titulo = models.TextField(
        _("Publication title"), blank=True, null=True)

    user_profile = models.ManyToManyField(UserProfile, blank=True, null=True)

    fecha = models.DateField(_("Date"), blank=True, null=True)

    nombre_publicacion = models.TextField(
        _("Publication name"), blank=True, null=True)

    volumen = models.CharField(
        _("Volume"), max_length=100, blank=True, null=True)

    numero = models.CharField(
        _("Number"), max_length=100, blank=True, null=True)

    pagina_inicial = models.CharField(
        _("First page"), max_length=100, blank=True, null=True)

    pagina_final = models.CharField(
        _("Last page"), max_length=100, blank=True, null=True)

    autores = models.TextField(_("Authors"), blank=True, null=True)

    isbn = models.CharField(_(u'ISBN'), max_length=150, blank=True, null=True)

    issn = models.CharField(_(u'ISSN'), max_length=150, blank=True, null=True)

    deposito_legal = models.CharField(
        _("Legal deposit"), max_length=150, blank=True, null=True)

    created_at = models.DateTimeField(_("Created"), auto_now_add=True)

    updated_at = models.DateTimeField(_("Updated"), auto_now=True)

    def __unicode__(self):
        return "%s" % self.titulo

    class Meta:
        verbose_name_plural = _("Publications")
        ordering = ['-fecha', 'titulo']
        abstract = True


class Articulo(Publicacion):

    @classmethod
    def remove_by_userprofile(cls, user_profile):
        user_profile.articulo_set.remove(
            *user_profile.articulo_set.all())
        cls.objects.filter(user_profile__isnull=True).delete()

    class Meta:
        verbose_name_plural = _("Articles")
        ordering = ['-fecha', 'titulo']


class Libro(Publicacion):

    @classmethod
    def remove_by_userprofile(cls, user_profile):
        user_profile.libro_set.remove(
            *user_profile.libro_set.all())
        cls.objects.filter(user_profile__isnull=True).delete()

    class Meta:
        verbose_name_plural = _("Books")
        ordering = ['-fecha', 'titulo']


class Capitulo(Publicacion):

    @classmethod
    def remove_by_userprofile(cls, user_profile):
        user_profile.capitulo_set.remove(
            *user_profile.capitulo_set.all())
        cls.objects.filter(user_profile__isnull=True).delete()

    class Meta:
        verbose_name_plural = _("Chapters of books")
        ordering = ['-fecha', 'titulo']


class Congreso(models.Model):
    """
        https://cvn.fecyt.es/editor/cvn.html?locale=spa#ACTIVIDAD_CIENTIFICA
    """

    objects = CongresoManager()

    user_profile = models.ManyToManyField(UserProfile, blank=True, null=True)

    titulo = models.TextField(_("Title"), blank=True, null=True)

    fecha_de_inicio = models.DateField(
        _("Date"), blank=True, null=True)

    fecha_de_fin = models.DateField(
        _("End date"), blank=True, null=True)

    nombre_del_congreso = models.TextField(
        _("Name of the conference"), blank=True, null=True)

    ciudad_de_realizacion = models.CharField(
        _("City"), max_length=500, blank=True, null=True)

    autores = models.TextField(_("Authors"), blank=True, null=True)

    fecha = models.DateField(_("Date"), blank=True, null=True)

    ambito = models.CharField(
        _("Field of the conference"), max_length=50, blank=True, null=True)

    otro_ambito = models.CharField(
        _("Another area"), max_length=250, blank=True, null=True)

    deposito_legal = models.CharField(
        _("Legal deposit"), max_length=150, blank=True, null=True)

    publicacion_acta_congreso = models.CharField(
        _("Publication in conference proceedings"), max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(_("Created"), auto_now_add=True)

    updated_at = models.DateTimeField(_("Updated"), auto_now=True)

    @classmethod
    def remove_by_userprofile(cls, user_profile):
        user_profile.congreso_set.remove(
            *user_profile.congreso_set.all())
        cls.objects.filter(user_profile__isnull=True).delete()

    def __unicode__(self):
        return "%s" % self.titulo

    class Meta:
        verbose_name_plural = _("Conferences")
        ordering = ['-fecha_de_inicio', 'titulo']


class ScientificExp(models.Model):

    objects = ScientificExpManager()

    user_profile = models.ManyToManyField(UserProfile, blank=True, null=True)

    titulo = models.CharField(
        _("Designation"), max_length=1000, blank=True, null=True)

    numero_de_investigadores = models.IntegerField(
        _("Number of researchers"), blank=True, null=True)

    autores = models.TextField(_("Authors"), blank=True, null=True)

    fecha_de_inicio = models.DateField(
        _("Start date"), blank=True, null=True)

    fecha_de_fin = models.DateField(
        _("End date"), blank=True, null=True)

    duracion = models.IntegerField(
        _("Duration (in days)"), blank=True, null=True)

    ambito = models.CharField(
        _("Scope"), max_length=50, blank=True, null=True)

    otro_ambito = models.CharField(
        _("Another area"), max_length=250, blank=True, null=True)

    cod_segun_financiadora = models.CharField(
        _("Code acc. to the funding institution"), max_length=150, blank=True, null=True)

    cuantia_total = models.CharField(
        _("Total amount"), max_length=19, blank=True, null=True)

    cuantia_subproyecto = models.CharField(
        _("Sub-project amount"), max_length=19, blank=True, null=True)

    porcentaje_en_subvencion = models.CharField(
        _("Percentage as grant"), max_length=19, blank=True, null=True)

    porcentaje_en_credito = models.CharField(
        _("Percentage as credit"), max_length=19, blank=True, null=True)

    porcentaje_mixto = models.CharField(
        _("Mixed percentage"), max_length=19, blank=True, null=True)

    created_at = models.DateTimeField(_("Created"), auto_now_add=True)

    updated_at = models.DateTimeField(_("Updated"), auto_now=True)

    def __unicode__(self):
        return u'%s' % self.titulo

    def save(self, *args, **kwargs):

        # If we update fecha_de_fin or duracion we must calculate the other
        # field. To check which one was modified we compare with old version.
        try:
            old = type(self).objects.get(pk=self.pk)
        except ObjectDoesNotExist:
            pass
        else:
            inicio_changed = (old.fecha_de_inicio != self.fecha_de_inicio
                              and self.fecha_de_inicio is not None)
            fin_changed = (old.fecha_de_fin != self.fecha_de_fin
                           and self.fecha_de_fin is not None)
            duracion_changed = (old.duracion != self.duracion and
                                self.duracion is not None)
            if inicio_changed or fin_changed:
                duracion = self.fecha_de_fin - self.fecha_de_inicio
                self.duracion = duracion.days
            elif duracion_changed:
                self.fecha_de_fin = (self.fecha_de_inicio +
                                     datetime.timedelta(days=self.duracion))
        # We do the save afterwards
        super(ScientificExp, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = _("Scientific Experience")
        ordering = ['-fecha_de_inicio', 'titulo']
        abstract = True


class Convenio(ScientificExp):
    """
    https://cvn.fecyt.es/editor/cvn.html?locale\
    =spa#EXPERIENCIA_CIENTIFICA_dataGridProyIDINoComp
    """

    @classmethod
    def remove_by_userprofile(cls, user_profile):
        user_profile.convenio_set.remove(
            *user_profile.convenio_set.all())
        cls.objects.filter(user_profile__isnull=True).delete()

    class Meta(ScientificExp.Meta):
        verbose_name_plural = _("Agreements")
        ordering = ['-fecha_de_inicio', 'titulo']


class Proyecto(ScientificExp):
    """
        https://cvn.fecyt.es/editor/cvn.html?locale\
        =spa#EXPERIENCIA_CIENTIFICA_dataGridProyIDIComp
    """

    @classmethod
    def remove_by_userprofile(cls, user_profile):
        user_profile.proyecto_set.remove(
            *user_profile.proyecto_set.all())
        cls.objects.filter(user_profile__isnull=True).delete()

    class Meta:
        verbose_name_plural = _("Projects")
        ordering = ['-fecha_de_inicio', 'titulo']


class TesisDoctoral(models.Model):
    """
        https://cvn.fecyt.es/editor/cvn.html?locale=spa#EXPERIENCIA_DOCENTE
    """

    objects = CvnItemManager()

    user_profile = models.ManyToManyField(UserProfile, blank=True, null=True)

    titulo = models.TextField(_("Project title"), blank=True, null=True)

    fecha = models.DateField(_("Date of reading"), blank=True, null=True)

    autor = models.CharField(
        _("Author"), max_length=256, blank=True, null=True)

    universidad_que_titula = models.CharField(
        _(u'University issuing the qualification'),
        max_length=500, blank=True, null=True
    )

    codirector = models.CharField(
        _("Co-director"), max_length=256, blank=True, null=True)

    created_at = models.DateTimeField(_("Created"), auto_now_add=True)

    updated_at = models.DateTimeField(_("Updated"), auto_now=True)

    @classmethod
    def remove_by_userprofile(cls, user_profile):
        user_profile.tesisdoctoral_set.remove(
            *user_profile.tesisdoctoral_set.all())
        cls.objects.filter(user_profile__isnull=True).delete()

    def __unicode__(self):
        return "%s" % self.titulo

    class Meta:
        verbose_name_plural = _("Doctoral Thesis")
        ordering = ['-fecha', 'titulo']


class Patente(models.Model):
    """
    https://cvn.fecyt.es/editor/cvn.html?locale=spa#EXPERIENCIA_CIENTIFICA
    """

    objects = CvnItemManager()

    user_profile = models.ManyToManyField(UserProfile, blank=True, null=True)

    titulo = models.TextField(_("Designation"), blank=True, null=True)

    fecha = models.DateField(_("Date"), blank=True, null=True)

    fecha_concesion = models.DateField(
        _("Concession date"), blank=True, null=True)

    num_solicitud = models.CharField(
        _("Request number"), max_length=100, blank=True, null=True)

    lugar_prioritario = models.CharField(
        _("Priority country"), max_length=100, blank=True, null=True)

    lugares = models.TextField(_("Countries"), blank=True, null=True)

    autores = models.TextField(_("Authors"), blank=True, null=True)

    entidad_titular = models.CharField(
        _("Owner entity"), max_length=255, blank=True, null=True)

    empresas = models.TextField(_("Companies"), blank=True, null=True)

    created_at = models.DateTimeField(_("Created"), auto_now_add=True)

    updated_at = models.DateTimeField(_("Updated"), auto_now=True)

    @classmethod
    def remove_by_userprofile(cls, user_profile):
        user_profile.patente_set.remove(
            *user_profile.patente_set.all())
        cls.objects.filter(user_profile__isnull=True).delete()

    def __unicode__(self):
        return "%s" % self.titulo

    class Meta:
        verbose_name_plural = _("Intellectual Properties")
        ordering = ['-fecha', 'titulo']


class OldCvnPdf(models.Model):

    user_profile = models.ForeignKey(UserProfile)

    cvn_file = models.FileField(_(u'PDF'), upload_to=get_old_cvn_path)

    uploaded_at = models.DateTimeField(_("Uploaded PDF"))

    created_at = models.DateTimeField(_("Created"), auto_now_add=True)

    updated_at = models.DateTimeField(_("Updated"), auto_now=True)

    def __unicode__(self):
        return '%s ' % self.cvn_file.name.split('/')[-1]

    class Meta:
        verbose_name_plural = _("Historical Normalized Curriculum Vitae")
        ordering = ['-uploaded_at']
