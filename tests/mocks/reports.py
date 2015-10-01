# -*- encoding: UTF-8 -*-

#
#    Copyright 2014-2015
#
#      STIC-Investigación - Universidad de La Laguna (ULL) <gesinv@ull.edu.es>
#
#    This file is part of Portal del Investigador.
#
#    Portal del Investigador is free software: you can redistribute it and/or
#    modify it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    Portal del Investigador is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with Portal del Investigador.  If not, see
#    <http://www.gnu.org/licenses/>.
#


@classmethod
def get_area_dept_404(cls, url, use_redis=True, timeout=None):
    if 'numero_documento' in url:
        return {'numero_documento': '54875596', 'letra':'B' }
    elif 'get_codpersona?nif' in url:
        return 38268
    elif "get_areas" in url:
        if 'get_areas?year' in url:
            return [
                {"nombre": "AREA ARIA", "codigo": 404,
                 "nombre_corto": "A.LING."}]
        else:
            return [
                {"miembros": [
                    {"cod_cce": 5610,
                     "cod_cce__descripcion": "Profesor Titular Universidad",
                     "cod_persona__apellido1": "MENDES",
                     "cod_persona__nombre": "MARCOS", "cod_persona": 1,
                     "cod_cce__descripcion_corta": "T.U.",
                     "cod_persona__apellido2": "LOZANO"},
                    {"cod_cce": 5610,
                     "cod_cce__descripcion": "Profesor Titular Universidad",
                     "cod_persona__apellido1": "CHINEA",
                     "cod_persona__nombre": "FRANCISCO", "cod_persona": 2,
                     "cod_cce__descripcion_corta": "T.U.",
                     "cod_persona__apellido2": "GARCIA"},
                    {"cod_cce": 5610,
                     "cod_cce__descripcion": "Profesor Titular Universidad",
                     "cod_persona__apellido1": "JONES",
                     "cod_persona__nombre": "LAURA", "cod_persona": 3,
                     "cod_cce__descripcion_corta": "T.U.",
                     "cod_persona__apellido2": "DE LEON"},
                    {"cod_cce": 6643,
                     "cod_cce__descripcion": "Profesor Contratado Doctor (1)",
                     "cod_persona__apellido1": "MARTIN",
                     "cod_persona__nombre": "ENRIQUE", "cod_persona": 4,
                     "cod_cce__descripcion_corta": "PCDT1",
                     "cod_persona__apellido2": "ORTIZ"},
                    {"cod_cce": 6643,
                     "cod_cce__descripcion": "Profesor Contratado Doctor (1)",
                     "cod_persona__apellido1": "STIGLITZ",
                     "cod_persona__nombre": "SIEGFRIED", "cod_persona": 5,
                     "cod_cce__descripcion_corta": "PCDT1",
                     "cod_persona__apellido2": "SCHULZE"}],
                    "unidad": {
                        "nombre": "AREA ARIA", "codigo": 404,
                        "nombre_corto": "A.LING."}}]
    elif "get_departamentos" in url:
        if 'get_departamentos?year' in url:
            return [
                {"nombre": "DEPARTAMENTO DEPARTAMENTAL", "codigo": 404,
                 "nombre_corto": "A.MATEMAT."}]
        else:
            return [
                {"miembros": [
                    {"cod_cce": 5610,
                     "cod_cce__descripcion": "Profesor Titular Universidad",
                     "cod_persona__apellido1": "DIAZ",
                     "cod_persona__nombre": "PABLO", "cod_persona": 6,
                     "cod_cce__descripcion_corta": "T.U.",
                     "cod_persona__apellido2": "ROMERO"},
                    {"cod_cce": 5610,
                     "cod_cce__descripcion": "Profesor Titular Universidad",
                     "cod_persona__apellido1": "SEXTO",
                     "cod_persona__nombre": "FELIPE", "cod_persona": 7,
                     "cod_cce__descripcion_corta": "T.U.",
                     "cod_persona__apellido2": "RODRIGUEZ"},
                    {"cod_cce": 5610,
                     "cod_cce__descripcion": "Profesor Titular Universidad",
                     "cod_persona__apellido1": "RUIZ",
                     "cod_persona__nombre": "VANESA", "cod_persona": 8,
                     "cod_cce__descripcion_corta": "T.U.",
                     "cod_persona__apellido2": "GARCIA"}],
                    "unidad": {
                        "nombre": "DEPARTAMENTO DEPARTAMENTAL", "codigo": 404,
                        "nombre_corto": "A.MATEMAT."}}]
