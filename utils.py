# -*- encondig: UTF-8 -*-

from django.core.exceptions import ObjectDoesNotExist
from cvn import settings as stCVN
from cvn.models import Articulo, Capitulo, Libro, UserProfile


def scientific_production_to_context(user_profile, context):
    try:
        user_profile.cvn
        context['Articulos'] = Articulo.objects.filter(
            user_profile=user_profile)
        context['Capitulos'] = Capitulo.objects.filter(
            user_profile=user_profile)
        context['Libros'] = Libro.objects.filter(
            user_profile=user_profile)
        context['Congresos'] = user_profile.congreso_set.all()
        context['Proyectos'] = user_profile.proyecto_set.all()
        context['Convenios'] = user_profile.convenio_set.all()
        context['TesisDoctorales'] = user_profile.tesisdoctoral_set.all()
        return True
    except ObjectDoesNotExist:
        return False


def cvn_to_context(user, context):
    try:
        context['cvn'] = user.cvn
        context['cvn_status'] = stCVN.CVN_STATUS[user.cvn.status][1]
    except ObjectDoesNotExist:
        return


def isdigit(obj):
    if type(obj) is str and obj.isdigit():
        return True
    else:
        return False


def noneToZero(value):
    return value if value is not None else 0


def calc_stats_department(self, members_list):
    dict_department = {}
    num_cvn_update = 0
    for member in members_list:
        try:
            user = UserProfile.objects.get(rrhh_code=member)
            if stCVN.CVN_STATUS[user.cvn.status][0] == 0:
                num_cvn_update += 1
        except ObjectDoesNotExist:
            pass
    dict_department['num_cvn_update'] = num_cvn_update
    dict_department['cvn_percent_updated'] = ((num_cvn_update * 100.0) /
                                              len(members_list))
    return dict_department
