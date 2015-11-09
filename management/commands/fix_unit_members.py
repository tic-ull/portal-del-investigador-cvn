# -*- encoding: UTF-8 -*-


from cvn.models import ReportMember, ReportDept, ReportArea
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings as st
import os
import unicodecsv
from optparse import make_option
from core.routers import in_database


class Command(BaseCommand):
    help = u'Fix memberships of departments'
    option_list = BaseCommand.option_list + (
        make_option(
            "-u",
            dest="unit",
            help="Specify the unit type ('dept' or 'area')",
        ),
        make_option(
            "--database",
            dest="database",
            help="Specify database to update",
        ),
        make_option(
            "--delete-empty",
            dest="delempty",
            default=False,
            action="store_true",
            help=" Delete departaments that no longer have members"
        )
    )


    def handle(self, *args, **options):
        if options['unit'] != 'dept' and options['unit'] != 'area':
            raise CommandError(
                'You must specify the of unit: '
                'python manage.py fix_unit_members -u {dept|area}'
            )
        unit = options['unit']
        database = (options['database']
                    if options['database'] is not None
                    else 'default')
        ReportUnit =  ReportDept if unit == 'dept' else ReportArea
        unit_field = 'COD_DEPARTAMENTO' if unit == 'dept' else 'COD_AREA'
        with open(os.path.join(st.BASE_DIR, unit + '_membership.csv')) as csv:
            reader = unicodecsv.DictReader(csv, delimiter=',')
            with in_database(database, write=True):
                for row in reader:
                    member = ReportMember.objects.get(
                        user_profile__rrhh_code=row['COD_PERSONA'])
                    department = ReportUnit.objects.get(code=row[unit_field])
                    member.department = department
                    member.save()
                if options['delempty']:
                    ReportDept.objects.filter(reportmember=None)

