# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from django.contrib.contenttypes.management import update_all_contenttypes


def add_view_cvn_reports_permission(apps, schema_editor):
    update_all_contenttypes()  # Fixes tests
    ContentType = apps.get_model('contenttypes.ContentType')
    Permission = apps.get_model('auth.Permission')
    content_type = ContentType.objects.get(app_label='cvn', model='cvn')
    Permission.objects.create(content_type=content_type,
                              codename='read_cvn_reports',
                              name='Can read cvn reports')


def delete_view_cvn_reports_permission(apps, schema_editor):
    apps.get_model('auth.Permission').objects.get(
        codename='read_cvn_reports').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cvn', '0005_auto_20150317_0922'),
    ]

    operations = [
        migrations.RunPython(add_view_cvn_reports_permission,
                             delete_view_cvn_reports_permission),
    ]