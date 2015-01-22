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

from .models import CVN, OldCvnPdf
from core import settings as st_core
from core.models import Log
from cvn import settings as st_cvn
from cvn import signals
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import pre_save, pre_delete

import datetime
import json


# Admin actions not calling model's delete() method
# https://code.djangoproject.com/ticket/10751
def cvn_delete_files(sender, instance, **kwargs):
    instance.cvn_file.delete(False)
    if hasattr(instance, 'xml_file'):
        instance.xml_file.delete(False)

pre_delete.connect(cvn_delete_files, sender=CVN)
pre_delete.connect(cvn_delete_files, sender=OldCvnPdf)


def log_status_cvn_changed(sender, instance, **kwargs):
    try:
        old_status = instance.__class__.objects.get(pk=instance.pk).status
    except ObjectDoesNotExist:
        # old_status = updated so the first time a user uploads a cvn, if it
        # is expired it will be considered a status change
        old_status = st_cvn.CVNStatus.UPDATED
    date_format = '%d/%m/%Y'
    Log.objects.create(
        user_profile=instance.user_profile,
        application=instance._meta.app_label.upper(),
        entry_type=st_core.LogType.CVN_UPDATED,
        date=datetime.datetime.now(),
        message=json.dumps({
            'status': st_cvn.CVN_STATUS[instance.status][1],
            'fecha': instance.fecha.strftime(date_format),
            'uploaded_at': instance.uploaded_at.strftime(date_format)
        })
    )
    if instance.status != old_status:
        signals.pre_cvn_status_changed.send(sender=None, cvn=instance)

pre_save.connect(log_status_cvn_changed, sender=CVN,
                 dispatch_uid='log_status_cvn_changed')
