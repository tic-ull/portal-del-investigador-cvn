# -*- encoding: UTF-8 -*-

from cvn.models import ReportMember, ReportDept, ReportArea
from django.core.management.base import BaseCommand, CommandError
from cvn.models import UserProfile
from core.routers import in_database
import unicodecsv
from optparse import make_option
from django.db import IntegrityError


class Command(BaseCommand):
    help = u'Load members from csv to be loaded on historical database'
    option_list = BaseCommand.option_list + (
        make_option(
            "--unit_type",
            dest="unit_type",
            help="Unit type (dept, area)",
        ),
        make_option(
            "--year",
            dest="year",
            help="Specify the year",
        ),
        make_option(
            "--path",
            dest="path",
            help="Specify the csv path",
        ),
    )

    def handle(self, *args, **options):
        self.check_args(options)
        path = options['path']
        year = options['year']
        unit_type = options['unit_type']
        if unit_type == 'area':
            unit_name = u'AREA'
            field_name = 'area'
            unit_code = u'COD_AREA'
            ReportUnit = ReportArea
        else:
            unit_name = u'DEPARTAMENTO'
            field_name = 'department'
            unit_code = u'COD_DPTO'
            ReportUnit = ReportDept

        with in_database(year, write=True):
            with open(path) as csv:
                reader = unicodecsv.DictReader(csv, delimiter=',')
                for row in reader:
                    try:
                        userp = UserProfile.objects.get(
                            rrhh_code=row[u'COD_PERSONA'])
                    except UserProfile.DoesNotExist:
                        document = row[u'DNI'].replace('-', '')
                        userp = UserProfile.get_or_create_user(
                            document, document)[0].profile
                        userp.rrhh_code = row[u'COD_PERSONA']
                        userp.user.first_name = row[u'NOMBRE']
                        userp.user.last_name = (row[u'PRIMER_APELLIDO'] +
                                                " " +
                                                row[u'SEGUNDO_APELLIDO'])[:30]
                        userp.user.save()
                        userp.save()

                    member_dict = {
                        'cce': row[u'CATEGORIA'],
                        'user_profile': userp
                    }
                    # Create the dept or area
                    unit = {'code': row[unit_code], 'name': row[unit_name]}
                    report_unit = ReportUnit.objects.get_or_create(
                        code=unit['code'], defaults=unit)[0]
                    #Create the ReportMember
                    try:
                        ReportMember.objects.update_or_create(
                            defaults={field_name: report_unit}, **member_dict)
                    except IntegrityError:
                        print(userp.documento)
                        import ipdb; ipdb.set_trace()


    def check_args(self, options):
        if options['year'] not in ('2012', '2013'):
            raise CommandError(
                'Option --year=<year> must be either 2012 or 2013'
            )
