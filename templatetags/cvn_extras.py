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

from cvn import settings as st_cvn
from django.utils.safestring import mark_safe
from django import template
from django.utils.translation import ugettext as _
import datetime
from django.conf import settings as st

register = template.Library()


@register.simple_tag
def messages_waiting():
    html = "switch($key) {\n"
    for i in range(len(st_cvn.MESSAGES_WAITING) - 1):
        html += ("\t" * 6 + "case %s:\n" % i)
        html += ("\t" * 7 + "$('#show').text(\"" +
                 _(st_cvn.MESSAGES_WAITING[i]) + "\");\n")
        html += ("\t" * 7 + "break;\n")
    html += (
        "\t" * 6 + "default:\n" +
        "\t" * 7 + "$('#show').text(\"" +
        _(st_cvn.MESSAGES_WAITING.values()[-1]) % {
            'support': st.SUPPORT,
            'email': st.EMAIL_SUPPORT
        } + "\");\n" + "\t" * 5 + "}")
    return mark_safe(html)


@register.filter(name='replace_current')
def replace_current(value, verbose=False):
    if value == datetime.date.today().year:
        return _('Current year') if verbose else _('current')
    else:
        return value
