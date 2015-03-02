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

CVN_SETTINGS_LOCAL = True
from .settings import *

# Enable translations in this file
_ = lambda s: s

# DJANGO CONSTANCE
st.CONSTANCE_CONFIG['EXPIRY_DATE'] = (
    datetime.date(2013, 12, 31), _(u'Expiry date for a CVN'))

# Default Entity
UNIVERSITY = _(u'Universidad de La Laguna')

# WS FECYT
FECYT_USER = "user"
FECYT_PASSWORD = "password"

# Unauthorized CVN Authors
CVN_PDF_AUTHOR_NOAUT = [u'FECYT - Author of Example', ]

# HISTORICAL REPORT
HISTORICAL_YEAR = '2013'

