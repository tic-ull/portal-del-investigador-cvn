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

from random import randint, uniform
from cvn import settings as st_cvn
import random
import datetime
import factory
from factory.fuzzy import (FuzzyChoice, FuzzyDate, FuzzyAttribute)


d = datetime.date(1940, 1, 1)


class ProfessionFactory(factory.Factory):
    des1_cargo = factory.Sequence(lambda n: 'Trabajo #{0}'.format(n))
    employer = FuzzyAttribute(lambda: 'Empresa #' + str(randint(0, 100)))
    f_toma_posesion = FuzzyDate(datetime.date(1940, 1, 1)).fuzz()
    f_hasta = FuzzyAttribute(lambda: random.choice(
        [None, FuzzyDate(d).fuzz()]))
    centro = FuzzyAttribute(lambda: random.choice(
        [None, 'Centro #' + str(randint(0, 100))]))
    departamento = FuzzyAttribute(lambda: random.choice(
        [None, 'Departamento #' + str(randint(0, 100))]))
    dedicacion = FuzzyChoice([True, False, None])

    class Meta:
        model = dict


class LearningPhdFactory(factory.Factory):
    des1_titulacion = factory.Sequence(lambda n: 'PHD recibido #{0}'.format(n))
    organismo = FuzzyAttribute(lambda: 'Universidad #' + str(randint(0, 100)))
    f_expedicion = FuzzyAttribute(
        lambda: random.choice([None, FuzzyDate(d).fuzz()]))

    class Meta:
        model = dict


class TeachingFactory(factory.Factory):
    asignatura = factory.Sequence(lambda n: 'Asignatura #{0}'.format(n))
    categ_anyo = FuzzyAttribute(
        lambda: u'Profesión #' + str(randint(0, 100)))
    tipo_estudio = FuzzyAttribute(lambda: random.choice(
        st_cvn.SUBJECT_TYPE.keys() +
        [u'Titulación #' + str(randint(0, 100))]))
    tipologia = FuzzyAttribute(lambda: random.choice(
        st_cvn.SUBJECT_TYPE.keys() +
        ['Tipo asignatura #' + str(randint(0, 100))]))
    curso = FuzzyAttribute(lambda: str(randint(1, 5)))
    plan_nomid = factory.Sequence(lambda n: u'Titulación #{0}'.format(n))
    university = FuzzyAttribute(lambda: random.choice(
        [None, st_cvn.UNIVERSITY, 'Universidad #' + str(randint(0, 100))]))
    departamento = FuzzyAttribute(lambda: random.choice(
        [None, 'Departamento #' + str(randint(0, 100))]))
    centro_nomid = FuzzyAttribute(lambda: random.choice(
        [None, 'Facultad #' + str(randint(0, 100))]))
    curso_inicio = FuzzyAttribute(lambda: str(randint(1990, 2020)))
    creditos = FuzzyAttribute(lambda: str(round(uniform(0.5, 15.5), 2)))

    class Meta:
        model = dict


class LearningFactory(factory.Factory):
    des1_titulacion = factory.Sequence(lambda n: u'Título #{0}'.format(n))
    des1_grado_titulacion = FuzzyAttribute(lambda: random.choice(
        st_cvn.OFFICIAL_TITLE_TYPE.keys() + ['GRADO', 'FP']))
    organismo = FuzzyAttribute(lambda: random.choice(
        [None, 'Universidad #' + str(randint(0, 100))]))
    f_expedicion = FuzzyAttribute(lambda: random.choice(
        [None, FuzzyDate(d).fuzz()]))

    class Meta:
        model = dict