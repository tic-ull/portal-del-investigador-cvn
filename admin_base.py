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

from .forms import UserProfileAdminForm, UploadCVNForm
from .models import OldCvnPdf, CVN
from core.widgets import FileFieldURLWidget
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class OldCvnPdfInline(admin.TabularInline):
    model = OldCvnPdf
    extra = 0
    readonly_fields = ('uploaded_at', )
    fields = ('cvn_file', 'uploaded_at')

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'cvn_file':
            kwargs['widget'] = FileFieldURLWidget
        return super(OldCvnPdfInline, self).formfield_for_dbfield(
            db_field, **kwargs)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class BaseUserProfileAdmin(admin.ModelAdmin):

    form = UserProfileAdminForm

    list_display = ('user', 'get_first_name', 'get_last_name', 'documento',
                    'rrhh_code', )

    list_filter = ('cvn__status', 'cvn__is_inserted', )

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = _("Name")

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = _("Surname")

    search_fields = ['user__username', 'documento', 'rrhh_code',
                     'user__first_name', 'user__last_name', ]

    def has_add_permission(self, request):
        return False


class BaseCvnInline(admin.TabularInline):
    model = CVN
    form = UploadCVNForm
    fields = ('cvn_file', 'xml_file', 'fecha', 'uploaded_at', 'status',
              'is_inserted')
    readonly_fields = ('fecha', 'uploaded_at', 'status', 'is_inserted')

    def has_delete_permission(self, request, obj=None):
        return False
