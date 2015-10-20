# -*- encoding: UTF-8 -*-


from cvn.models import ReportMember, ReportDept, ReportArea
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings as st
import os
import unicodecsv
from optparse import make_option


class Command(BaseCommand):
    help = u'Fix memberships of departments'
    option_list = BaseCommand.option_list + (
        make_option(
            "-u",
            dest="unit",
            help="Specify the unit type ('dept' or 'area')",
        ),
    )

    def handle(self, *args, **options):
        if options['unit'] != 'dept' and options['unit'] != 'area':
            raise CommandError(
                'You must specify the of unit: '
                'python manage.py fix_unit_members -u {dept|area}'
            )
        unit = options['unit']
        ReportUnit =  ReportDept if unit == 'dept' else ReportArea
        with open(os.path.join(st.BASE_DIR, unit + '_membership.csv')) as csv:
            reader = unicodecsv.DictReader(csv, delimiter=',')
            for row in reader:
                member = ReportMember.objects.get(
                    user_profile__rrhh_code=row['COD_PERSONA'])
                department = ReportUnit.objects.get(code=row[
                    'COD_DEPARTAMENTO'])
                member.department = department
                member.save()
