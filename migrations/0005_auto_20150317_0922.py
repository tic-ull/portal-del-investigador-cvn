# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from django.contrib.contenttypes.management import update_all_contenttypes


def add_view_university_report_permission(apps, schema_editor):
    update_all_contenttypes()  # Fixes tests
    ContentType = apps.get_model('contenttypes.ContentType')
    Permission = apps.get_model('auth.Permission')
    content_type = ContentType.objects.get(app_label='cvn', model='cvn')
    Permission.objects.create(content_type=content_type,
                              codename='view_university_report',
                              name='Can access university report')


def delete_view_university_report_permission(apps, schema_editor):
    apps.get_model('auth.Permission').objects.get(
        codename='view_university_report').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cvn', '0004_oldcvnpdf'),
    ]

    operations = [
        migrations.RunPython(add_view_university_report_permission,
                             delete_view_university_report_permission),
    ]
