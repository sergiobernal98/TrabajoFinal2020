# -*- coding: utf-8 -*-
# Archivo: xxx.py
# Autor: Elena Aragoneses de la Rubia y Sergio Bernal Sanchez
# Fecha: 10/01/2020
# Descripcion: Ejercicio tranajo final. Realizar tareas de geoprocesamiento (consultas)
# cin PyQgis

"""
Parte 1 del ejericio 2 de la asignatura Fundamentos de análisis
y razonamiento espacial
con PyQGIS (consultas tematicas y espaciales)
"""

import os

# Importar clase para capas vectoriales
from qgis.core import (QgsVectorLayer)

# Funcion para abrir capas vectoriales y ver si existen
def instanciar(nombre_capa, nombre_instancia):
    nombre_instancia = QgsVectorLayer(dir, nombre_capa, "ogr")
    if not nombre_instancia.isValid():  # None si no es valida
        print("No se puede cargar la capa especificada")

# Etablecer espacio de trabajo
dir = "C:\\Users\\elena\\Desktop\\Universidad\\MasterTIGUAH\\Programacion\\Trabajofinal\\Material_practica\\capas_entrada"

lista_shp = []
lista_archivos = os.listdir()  # Lista de las capas en el espacio de trabajo

# Quedarnos solo con los shp
for archivo in lista_archivos:
    if archivo[-4:] == ".shp":
        # Quitar la extension
        capa_sin_extension = archivo[:-4]
        lista_shp.append(capa_sin_extension)

# Intanciar capas vectoriales
lista_capas_inst = []
for capa_shp in lista_shp:
    nombre_salida = capa_shp + "inst"
    # Usamos esta funcion en vez de  addVectorLayer() porque no queremos verlas
    # en qgis ahora
    instanciar(capa_shp, nombre_salida)
    lista_capas_int.append()
    
# Abrir tambien el csv (tabla) separado por punto y comas
# Usamos esta forma para importar solo un dbf (no esta asociado a shp) y no todos
nombre_archivo_csv = "Brussels_AverageAge"
Brussels_AverageAge_inst = QgsVectorLayer(dir, nombre_archivo_csv, "delimitedtext")

# Ver la proyeccion de cada capa shp
# para si no es EPSG 31370 proyectarla a ese EPSG
# da informacion del sistema de coordenadas que se indica
# Solo se puede hacer sobre capas activdas
# A PARTIR DE AQUI NO SALE
for capas_int in lista_capas_int:
    proyeccion = qgis.utils.iface.activeLayer().crs().authid()
    print(capa_int, ":", proyeccion)
    if proyeccion != "EPSG:31370":
        parameter = {'INPUT': layer, 'TARGET_CRS': 'EPSG:31370',
                 'OUTPUT': 'memory:Reprojected'}

        resultado = processing.run('native:reprojectlayer', parameter)
        

    