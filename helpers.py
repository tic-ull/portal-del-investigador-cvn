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

import datetime
import hashlib
import os


def _get_md5_path(keyword):
    md5 = hashlib.md5(keyword).hexdigest()[0:2]
    return "cvn/%s/" % md5


# Ignores original filename. Useful when the file comes from the client
# Do not change signature http://goo.gl/tbTq8g
def get_automatic_cvn_path(instance, filename):
    return os.path.join(
        _get_md5_path(instance.user_profile.documento),
        instance.user_profile.documento,
        u'CVN-%s.pdf' % instance.user_profile.documento
    )


# Uses original filename. Useful when the file is created using FileField.save()
# Do not change signature http://goo.gl/tbTq8g
def get_manual_cvn_path(instance, filename):
    return os.path.join(_get_md5_path(instance.user_profile.documento),
                        instance.user_profile.documento, filename)


# Do not change signature http://goo.gl/tbTq8g
def get_old_cvn_path(instance, filename):
    return os.path.join(_get_md5_path(instance.user_profile.documento),
                        instance.user_profile.documento, 'old', filename)


class DateRange:
    MIN_DATE = datetime.date(datetime.MINYEAR, 1, 1)
    MAX_DATE = datetime.date(datetime.MAXYEAR, 12, 31)

    def __init__(self, start_date=None, end_date=None):
        self.start_date = self.MIN_DATE if start_date is None else start_date
        self.end_date = self.MAX_DATE if end_date is None else end_date

    def intersect(self, b):
        return ((self.start_date <= b.start_date <= self.end_date)
                or (b.start_date <= self.start_date <= b.end_date))
