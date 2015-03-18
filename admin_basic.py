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

from django.contrib import admin
from .admin_base import OldCvnPdfInline, BaseUserProfileAdmin, BaseCvnInline
from core.admin_basic import basic_admin_site
from core.models import UserProfile, Log
from core.widgets import FileFieldURLWidget
import core.settings as st_core


class CvnInline(BaseCvnInline):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'xml_file' or db_field.name == 'cvn_file':
            kwargs['widget'] = FileFieldURLWidget
        return super(CvnInline, self).formfield_for_dbfield(db_field, **kwargs)


class CvnLogInline(admin.TabularInline):
    model = Log
    fields = ('date', 'message')
    readonly_fields = fields

    def get_queryset(self, request):
        qs = super(CvnLogInline, self).get_queryset(request)
        return qs.filter(entry_type=st_core.LogType.CVN_UPDATED.value,
                         application='CVN')


class UserProfileAdmin(BaseUserProfileAdmin):
    inlines = [CvnInline, OldCvnPdfInline, CvnLogInline]
    readonly_fields = ['user', 'rrhh_code', 'documento']

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context.update({
            'show_save_and_continue': False,
            'show_save': False,
        })
        return super(UserProfileAdmin, self).change_view(request, object_id,
            form_url, extra_context=extra_context)

    def get_actions(self, request):
        """ Remove action delete object from list of actions """
        actions = super(UserProfileAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

basic_admin_site.register(UserProfile, UserProfileAdmin)
