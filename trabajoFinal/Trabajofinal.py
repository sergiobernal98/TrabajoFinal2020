# -*- coding: utf-8 -*-
# Archivo: xxx.py
# Autor: Elena Aragoneses de la Rubia y Sergio Bernal Sanchez
# Fecha: 10/01/2020
# Descripcion: Ejercicio trabajo final. Realizar tareas de geoprocesamiento (instanciar, proyectar, consultas)
# con PyQgis

"""
Parte 1 del ejericio 2 de la asignatura Fundamentos de análisis
y razonamiento espacial
con PyQGIS (consultas tematicas y espaciales)
"""

import qgis, os, ogr
from qgis.core import *
from qgis import processing

# Funcion para abrir capas vectoriales y ver si existen
# No usamos utils.iface.activeLayer porque eso es para seleccionar las layers
# de la leyenda del proyecto de qgis
def instanciar(nombre_capa):
    """
    Instancia capas vectoriales.
    Argumetnos:
    nombre_capa es el nombre de la capa con extension a instanciar
    """
    
    ruta = directorio + "\\" + nombre_capa
    nombre_instancia = QgsVectorLayer(ruta, nombre_capa, "ogr")
    return nombre_instancia

# Funcion para hacer Join
def join(instancia_1, instancia_2, campo_join_instancia_1, campo_join_instancia_2):
    """
    Hace el join entre una capa ectorial y tabla o entre
    2 capas vectoriales
    
    Argumetnos: 
    instancia_1 es la capa en la que se efectua el join
    instancia_2 es el otro elemnto que participa en el join
    campo_join_instancia_1 es el campo para hacer el join para instancia_1
    campo_join_instancia_2 es el campo para hacer el join para instancia_2
    """
    
    joinObject = QgsVectorLayerJoinInfo()
    joinObject.setJoinFieldName(campo_join_instancia_2)
    joinObject.setTargetFieldName(campo_join_instancia_1)
    joinObject.setUsingMemoryCache(True)
    joinObject.setJoinLayer(instancia_2)
    instancia_1.addJoin(joinObject)

# Funcion para exportar resultado en shp
def exportar(layer, nombre_shp_salida):
    """
    Exportar el resultado como un shp.
    La proyeccion de la capa exportada es la misma que la que tiene
    la capa sobre la que se hace la seleccion
    Argumentos:
    layer: capa instanciada
    nombre_shp_salida = nombre shp con resultado exportacion sin extension
    """
    
    shp_salida = nombre_shp_salida + ".shp"
    ruta_salida = directorio + "\\" + shp_salida
    encoding = "windows-1252"
    formato_salida = "ESRI Shapefile"
    QgsVectorFileWriter.writeAsVectorFormat(layer, ruta_salida, encoding, layer.crs(), formato_salida, onlySelected=True)

# Etablecer espacio de trabajo
directorio = "C:\\Users\\elena\\Desktop\\Universidad\\MasterTIGUAH\\Programacion\\Trabajofinal\\Material_practica\\capas_entrada"
os.chdir(directorio)

lista_shp = []
lista_archivos = os.listdir()  # Lista de las capas en el espacio de trabajo

# Abrir tambien el csv (tabla) separado por punto y comas
# Usamos esta forma para importar solo un dbf (no esta asociado a shp) y no todos

nombre_archivo_csv = "Brussels_AverageAge.csv"
uri = "file:///" + directorio + "\\" + nombre_archivo_csv + "?delimiter=;"
# El csv se instancia diferente
# Se carga como una tabla usado el proveedor delimitedtext
# Instancia
Brussels_AverageAge = QgsVectorLayer(uri, nombre_archivo_csv, "delimitedtext")
"""
print ("*" * 20)
for archivo in lista_archivos:
    if archivo[-4:] == ".shp": # Quedarnos solo con los shp
        if archivo[:-5] == "repr_":
            # Para no meter en el bucle las capas reproyectadas creadas
            pass
        else:
            # Quitar la extension
            lista_shp.append(archivo)
            
            capa_sin_extension = archivo[:-4]  # El nombre de la capa sin extension
            
            # Usamos esta funcion en vez de  addVectorLayer() porque no queremos verlas
            # en qgis ahora
            instancia = instanciar(archivo)
            proyeccion = instancia.crs().authid()  # Devuelve str con EPSG:xxx
            
            # Proyectar
            # Ver la proyeccion de cada capa shp
            # para si no es EPSG 31370 proyectarla a ese EPSG

            crs = QgsCoordinateReferenceSystem()
            if proyeccion != "EPSG:31370":
                # Si el crs de entrada no es 31370
                # O no tiene proyeccion especificada
                
                # Necesario decir que la capa de salida es shp (sino formato 
                # predeterminado: geopackage)
                nombre_reproyectada = "repr_" + capa_sin_extension + ".shp"
                # Los parametros se almacenan en un diccionario
                parameter = {"INPUT": archivo, "TARGET_CRS": "EPSG:31370",
                     "OUTPUT": nombre_reproyectada}
                     
                resultado = processing.run('native:reprojectlayer', parameter)
                nombre_capa_reproyectada_extension = resultado["OUTPUT"]

                # Esto ha creado una nueva capa, luego se debe instanciar
                instancia = instanciar(nombre_capa_reproyectada_extension)
        
                proyeccion_final = instancia.crs().authid()
                
                print ("De {0} con {1} se ha creado {2} con {3}".\
                format(archivo, proyeccion, nombre_capa_reproyectada_extension, proyeccion_final))

            elif proyeccion == "EPSG:31370":
                # No hace falta hacer nada si ya tien el EPSG deseado
                pass
                
                print ("La capa {0} ya tenia el EPSG correcto ({1}). No se ha reproyectado."\
                .format(archivo, proyeccion))

print ("*" * 20)

# Siguente paso: hacer joins
# 1. Entre capa densidad de poblacion y tabla
# 2. Entre el resultado del anterior join y Average_Income.shp
# Se deben instanciar diferenciadas las capas que participan en el join
# El csv ya se instancio arriba de forma diferente
shp1 = "repr_Population_Density_Brussels.shp"
Population_Density_Brussels = instanciar(shp1)
shp2 = "repr_Average_Income.shp"
Average_Income = instanciar(shp2)

# Campos para hacer los join
shpField="MUNC"
csvField="Munc"
# Hacer los joins (se concatenan y se alamacena todo en la misma capa)
join(Population_Density_Brussels, Brussels_AverageAge, shpField, csvField)
join(Population_Density_Brussels, Average_Income, shpField, shpField)

# Se puede observar como se han añadido nuevos campos de la tabla (ejemplo con join 1)
print ("Campos tras el join en {0}:".format(shp1))
for field in Population_Density_Brussels.fields():
    print(field.name(), field.typeName())

# SELECCIONES

# Seleccion por expresion
# Seleccion 1. Seleccion de carreteras rapidas y ferrocarriles de Bruselas
# Necesito instanciar la capa de Bruselas
shp3 = "BrusselsCity.shp"
Bruselas = instanciar(shp3)

# Condicion para la seleccion 1. Se usa or porque puede ser ambas
exp_selec_1 = "\"ITEM\" = 'Railways and associated land' or \"ITEM\" \
    = 'Fast transit roads and associated land'"
# Seleccion por atributos
Bruselas.selectByExpression(exp_selec_1, QgsVectorLayer.SetSelection)
# Funcion seleccion por atributos y exportar resultado como shp
shp_salida = "RoadRailways"
exportar(Bruselas, shp_salida)

# Para borrar la seleccion
Bruselas.removeSelection()
# Porque despues se parte desde 0 con esta capa

# Seleccion 2. Seleccion de caracteristicas de la poblacion
# del resultado del join
# Se usa and en vez de or porque se queiren las 3 condiciones a la vez
exp_selec_2 = "\"Density_km\" > 2000 and \"Brussels_AverageAge.csv_AverageAge\"\
    < 37 and \"repr_Average_Income.shp_I_hab_10\" > 10000"
Population_Density_Brussels.selectByExpression(exp_selec_2, QgsVectorLayer.SetSelection)
shp_salida = "muni_select"
exportar(Population_Density_Brussels, shp_salida)

# Seleccion 3. Seleccion de condiciones de la ciudad Bruselas
exp_selec_3 = "(\"ITEM\" = 'Discontinuous Low Density Urban Fabric (S.L. : 10% - 30%)' \
    or \"ITEM\" = 'Discontinuous Medium Density Urban Fabric (S.L. : 30% - 50%)' or \"ITEM\"\
    = 'Land without current use') and (\"SHAPE_Area\" >= 500)"
Bruselas.selectByExpression(exp_selec_3, QgsVectorLayer.SetSelection)
shp_salida = "land_select"
exportar(Bruselas, shp_salida)

# Seleccion 4. Seleccion por localizacion
# Se usa algoritmo de procesameinto: qgis:selectbylocation
# Instancio las capas necesarias
shp4 = "muni_select.shp"
muni_select = instanciar(shp4)
shp5 = "land_select.shp"
land_select = instanciar(shp5)
# parcelas de land_select.shp dentro (6) de muni_select
# Los parametros se almacenan en un diccionario
parameter = {"INPUT": land_select, "PREDICATE": 6,
     "INTERSECT": muni_select, "OUTPUT": "TEMPORARY_OUTPUT"}
processing.run("qgis:selectbylocation", parameter)
shp_salida = "land_muni_select"
exportar(land_select, shp_salida)

# Buffer de 499.999 m desde RoadRailways
# Se usa algortimo de procesameinto: qgis.buffer
shp6 = "RoadRailways.shp"  # Instancio
RoadRailways = instanciar(shp6)
parameter = {"INPUT": RoadRailways,"DISTANCE": 499.999,\
    "DISSOLVE": True, "OUTPUT": "buffer.shp"}
processing.run("qgis:buffer", parameter)
"""
# Seleccion 5. Seleccion por localizacion
# Seleccionar parcelas de land_muni_select a menos de 500 m de carreteras
# (usando el buffer)
shp7 = "buffer.shp"
buffer = instanciar(shp7)
shp8= "land_muni_select.shp"
land_muni_select = instanciar(shp8)
parameter = {"INPUT": land_muni_select, "PREDICATE": 0,
     "INTERSECT": buffer, "OUTPUT": "TEMPORARY_OUTPUT"}
processing.run("qgis:selectbylocation", parameter)
# Como en verdad se quiere seleccionar las que quedan a mas
# de 500 m se debe hacer el inverso de esta seleccion
land_muni_select.invertSelection()
shp_salida = "Parcels_dist_transport"
exportar(land_muni_select, shp_salida)