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

from functools import wraps
from django.http import Http404


def user_can_view_reports(view=None, user=None):

    def _user_can_view_reports(user):
        if user.has_perm('cvn.read_cvn_reports'):
            return True
        return False

    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if _user_can_view_reports(request.user):
            return view(request, *args, **kwargs)
        else:
            raise Http404

    if view is not None:
        return wrapper
    else:
        return _user_can_view_reports(user)