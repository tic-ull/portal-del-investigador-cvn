# -*- encoding: UTF-8 -*-

from django.core.management.base import BaseCommand#, CommandError
from optparse import make_option
import glob
import commands
import codecs
import unicodecsv as csv
import os

class Command(BaseCommand):
    help = u'Crea un .csv con los investigadores raros'
    option_list = BaseCommand.option_list + (
        make_option(
            "-p",
            dest="path",
            help="Specify the path where pdfs are",
        ),
    )

    def handle(self, *args, **options):
        ruta = options['path']
        lista = glob.glob(os.path.join(ruta, "*.pdf"))
        self.adaptar_txt(ruta, lista)

    def convert_pdf_to_txt(self, path):
        commands.getoutput("pdftotext " + path)      # se crea un txt por cada pdf

    def adaptar_txt(self, ruta, lista):

        archivo_general = open(os.path.join(ruta, "membership.csv"), 'w')
        writer = csv.writer(archivo_general, delimiter=',')
        writer.writerow(['NOMBRE', 'PRIMER APELLIDO', 'SEGUNDO APELLIDO', 'CATEGORIA', 'DEPARTAMENTO'])
        for path in lista:
            self.convert_pdf_to_txt(path)
            fichero_texto = path.replace(".pdf", ".txt")    # reemplaza el nombre del fichero por txt
            archivo = codecs.open( fichero_texto, "r", "utf-8")
            departamento = archivo.readline()
            fin = False
            while not fin:
                linea = archivo.readline()
                if 'investigadores:' in linea:
                    num_invest = int(linea.split(':')[1])
                elif u'CATEGORÍA' in linea:
                    linea = archivo.readline()
                    fin  = True
            pagina = 1
            for j in range(num_invest):
                nombre = archivo.readline()
                aux = archivo.readline()
                if departamento in aux or departamento in nombre:
                    pagina += 1
                    if pagina > 2:
                        archivo.readline()
                        archivo.readline()
                    archivo.readline()
                    archivo.readline()
                    archivo.readline()
                    archivo.readline()
                    archivo.readline()
                    archivo.readline()
                    archivo.readline()
                    archivo.readline()
                    nombre = archivo.readline()
                    archivo.readline()
                    primer_apellido = archivo.readline()
                    archivo.readline()
                    segundo_apellido = archivo.readline()
                    archivo.readline()
                    categoria = archivo.readline()
                    archivo.readline()
                else:
                    primer_apellido = archivo.readline()
                    archivo.readline()
                    segundo_apellido = archivo.readline()
                    archivo.readline()
                    categoria = archivo.readline()
                    archivo.readline()
                text = [nombre[:-1], primer_apellido[:-1], segundo_apellido[:-1], categoria[:-1], departamento[:-1]]
                writer.writerow(text)
            archivo.close()
        commands.getoutput("rm " + ruta + "*.txt")
        archivo_general.close()

