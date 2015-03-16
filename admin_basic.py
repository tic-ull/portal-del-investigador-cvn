# -*- encoding: UTF-8 -*-

#
#    Copyright 2015
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

from .models import CVN, OldCvnPdf
from core.admin_basic import basic_admin_site
from core.models import UserProfile
from core.widgets import FileFieldURLWidget
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class CvnInlineReadonly(admin.StackedInline):
    model = CVN
    fields = ('cvn_file', 'xml_file')

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'xml_file' or db_field.name == 'cvn_file':
            kwargs['widget'] = FileFieldURLWidget
        return super(CvnInlineReadonly, self).formfield_for_dbfield(
            db_field, **kwargs)


class OldCvnPdfInline(admin.StackedInline):

    model = OldCvnPdf

    extra = 0

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'cvn_file':
            kwargs['widget'] = FileFieldURLWidget
        return super(OldCvnPdfInline, self).formfield_for_dbfield(
            db_field, **kwargs)

    readonly_fields = ('uploaded_at', )

    fields = ('cvn_file', 'uploaded_at')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class UserProfileAdmin(admin.ModelAdmin):

    list_display = ('user', 'get_first_name', 'get_last_name', 'documento',
                    'rrhh_code', )

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = _(u'Nombre')

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = _(u'Apellidos')

    search_fields = ['user__username', 'documento', 'rrhh_code',
                     'user__first_name', 'user__last_name', ]

    inlines = [CvnInlineReadonly, OldCvnPdfInline]
    readonly_fields = ['user', 'rrhh_code', 'documento']

    def has_add_permission(self, request):
        return False

basic_admin_site.register(UserProfile, UserProfileAdmin)
