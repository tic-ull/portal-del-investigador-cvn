# # -*- encoding: UTF-8 -*-
#
#
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
        with in_database(options['year'], write=True):
            self.check_args(options)
            with open(options['path']) as csv:
                reader = unicodecsv.DictReader(csv, delimiter=',')
                ReportArea.objects.all().delete()
                ReportDept.objects.all().delete()
                ReportMember.objects.all().delete()
                for row in reader:
                    try:
                        userp = UserProfile.objects.get(
                            rrhh_code=row[u'COD_PERSONA'])
                    except UserProfile.DoesNotExist:
                        #import ipdb; ipdb.set_trace()
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

                    if row[u'COD_DPTO']:
                        department = {
                            'code': row[u'COD_DPTO'],
                            'name': row[u'DEPARTAMENTO']
                        }

                        report_dept = ReportDept.objects.get_or_create(
                            code=department['code'], defaults=department)[0]
                        member_dict['department'] = report_dept

                    if row['COD_AREA']:
                        area = {
                            'code': row[u'COD_AREA'],
                            'name': row[u'AREA']
                        }

                        report_area = ReportArea.objects.get_or_create(
                            code=area['code'], defaults=area)[0]
                        member_dict['area'] = report_area
                    try:
                        ReportMember.objects.create(**member_dict)
                    except IntegrityError:
                        import ipdb; ipdb.set_trace()


    def check_args(self, options):
        if options['year'] not in ('2012', '2013'):
            raise CommandError(
                'Option --year=<year> must be either 2012 or 2013'
            )
