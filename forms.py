# -*- encoding: UTF-8 -*-

from cvn import settings as st_cvn
from django import forms
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from models import FECYT, CVN, OldCvnPdf

import mimetypes


class UploadCVNForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        if 'instance' in kwargs and kwargs['instance'] is not None:
            self.user = kwargs['instance'].user_profile.user
        if 'data' in kwargs and 'user' in kwargs['data']:
            try:
                self.user = User.objects.get(pk=kwargs['data']['user'].pk)
            except:
                self.user = User.objects.get(pk=kwargs['data']['user'])
        if 'initial' in kwargs and 'cvn_file' in kwargs['initial']:
            if 'data' not in kwargs:
                kwargs['data'] = {}
            kwargs['data']['cvn_file'] = kwargs['initial']['cvn_file']
        super(UploadCVNForm, self).__init__(*args, **kwargs)

    def clean_cvn_file(self):
        try:
            cvn_file = self.cleaned_data['cvn_file']
        except:
            cvn_file = self.data['cvn_file']
        if mimetypes.guess_type(cvn_file.name)[0] != st_cvn.PDF:
            raise forms.ValidationError(
                _(u'El CVN debe estar en formato PDF.'))
        (self.xml, error) = FECYT.pdf2xml(cvn_file)
        if not self.xml:
            raise forms.ValidationError(_(st_cvn.ERROR_CODES[error]))
        return cvn_file

    @transaction.atomic
    def save(self, commit=True):
        (cvn_old, old_cvn_file) = CVN.remove_cvn_by_userprofile(self.user.profile)
        if old_cvn_file is not None:
            OldCvnPdf(user_profile=cvn_old.user_profile,
                      cvn_file=SimpleUploadedFile(old_cvn_file.split('/')[-1],
                                                  open(old_cvn_file).read(),
                                                  content_type=st_cvn.PDF),
                      uploaded_at=cvn_old.uploaded_at).save()
        cvn = super(UploadCVNForm, self).save(commit=False)
        cvn.user_profile = self.user.profile
        cvn.update_fields(self.xml, commit)
        if commit:
            cvn.save()
        return cvn

    class Meta:
        model = CVN
        fields = ['cvn_file']
