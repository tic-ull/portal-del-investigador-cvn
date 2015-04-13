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

from .models import CVN, UserProfile
from cvn import settings as st_cvn
from django import forms
from django.contrib.auth.models import User
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from PyPDF2 import PdfFileReader
from PyPDF2.utils import PdfReadError

import fecyt
import mimetypes


class UploadCVNForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.xml = None
        if 'instance' in kwargs and kwargs['instance'] is not None:
            self.user = kwargs['instance'].user_profile.user
        if 'data' in kwargs and 'user' in kwargs['data']:
            try:
                self.user = User.objects.get(pk=kwargs['data']['user'].pk)
            except AttributeError:
                self.user = User.objects.get(pk=kwargs['data']['user'])
        if 'initial' in kwargs and 'cvn_file' in kwargs['initial']:
            if 'data' not in kwargs:
                kwargs['data'] = {}
            kwargs['data']['cvn_file'] = kwargs['initial']['cvn_file']
        super(UploadCVNForm, self).__init__(*args, **kwargs)

    def clean_cvn_file(self):
        cvn_file = self.cleaned_data['cvn_file']
        if mimetypes.guess_type(cvn_file.name)[0] != "application/pdf":
            raise forms.ValidationError(
                _(u'El CVN debe estar en formato PDF.'))
        cvn_file.open()
        # Author
        try:
            pdf = PdfFileReader(cvn_file)
            pdf_info = pdf.getDocumentInfo()
            if ('/Author' in pdf_info and
                    pdf_info['/Author'] in st_cvn.CVN_PDF_AUTHOR_NOAUT):
                raise forms.ValidationError(
                    _(u'El CVN debe estar generado desde el Editor CVN de la FECYT')
                )
        except PdfReadError:
            raise forms.ValidationError(
                _(u'El CVN debe estar en formato PDF.'))
        # FECYT
        cvn_file.seek(0)
        (self.xml, error) = fecyt.pdf2xml(cvn_file.read(), cvn_file.name)
        if not self.xml:
            raise forms.ValidationError(_(st_cvn.ERROR_CODES[error]))
        return cvn_file

    @transaction.atomic
    def save(self, commit=True):
        CVN.remove_cvn_by_userprofile(self.user.profile)
        cvn = super(UploadCVNForm, self).save(commit=False)
        cvn.user_profile = self.user.profile
        cvn.initialize_fields(xml=self.xml, commit=False)
        if commit:
            cvn.save()
        return cvn

    class Meta:
        model = CVN
        fields = ['cvn_file']


def get_range_of_years_choices():
    choices = [(x, x) for x in reversed(range(
        st_cvn.RANGE_OF_YEARS[0], st_cvn.RANGE_OF_YEARS[1]))]
    return choices


class GetDataCVNULL(forms.Form):

    year = forms.ChoiceField(
        choices=get_range_of_years_choices(), required=False)

    start_year = forms.ChoiceField(
        choices=get_range_of_years_choices(), required=False)

    end_year = forms.ChoiceField(
        choices=get_range_of_years_choices(), required=False)

    def clean_end_year(self):
        start_year = self.cleaned_data['start_year']
        end_year = self.cleaned_data['end_year']
        if start_year and end_year:
            if int(start_year) > int(end_year):
                raise forms.ValidationError(
                    _(u'El año inicial no puede ser mayor que el año final'))
        return end_year


class UserProfileAdminForm(forms.ModelForm):
    first_name = forms.CharField(
        label=_('Nombre'),
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    last_name = forms.CharField(
        label=_('Apellidos'),
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    class Meta:
        model = UserProfile

    def __init__(self, *args, **kwargs):
        super(UserProfileAdminForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
