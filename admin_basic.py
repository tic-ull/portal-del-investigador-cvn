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

from core.admin_basic import basic_admin_site
from core.models import UserProfile
from core.widgets import FileFieldURLWidget
from .admin_base import OldCvnPdfInline, BaseUserProfileAdmin, BaseCvnInline


class CvnInline(BaseCvnInline):
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'xml_file' or db_field.name == 'cvn_file':
            kwargs['widget'] = FileFieldURLWidget
        return super(CvnInline, self).formfield_for_dbfield(db_field, **kwargs)


class UserProfileAdmin(BaseUserProfileAdmin):
    inlines = [CvnInline, OldCvnPdfInline]
    readonly_fields = ['user', 'rrhh_code', 'documento']

basic_admin_site.register(UserProfile, UserProfileAdmin)
