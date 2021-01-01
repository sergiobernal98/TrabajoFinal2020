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

Problema: encontrar la ubicacion adecuada para construir viviendas
para familias jovenes con renta media cerca de esucelas
primarias en la ciudad de Bruselas
"""

import os, ogr
from qgis import processing
from qgis.core import *
from qgis.PyQt.QtCore import QVariant


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
    
    Argumentos: 
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


def indice_campo(capa, campo):
    """
    Obtener indice de campos de una capa
    
    Argumentos:
    capa: instancia de la capa
    campo: nombre del campo
    """
    
    fields = capa.fields()
    index = fields.indexFromName(campo)
    return index
    
    
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
    encoding = layer.dataProvider().encoding()  # coger el encoding de la capa
    formato_salida = "ESRI Shapefile"
    QgsVectorFileWriter.writeAsVectorFormat(layer, ruta_salida, encoding, \
        layer.crs(), formato_salida, onlySelected=True)
    print ("Se ha creado {0} en el espacio de trabajo establecido".format(shp_salida))


# Funcion seleccion por localizacion
def selec_localizacion(capa_entrada1, capa_entrada2, predicado):
    """"
    Seleccion por localizacion
    
    Argumentos:
    capa_entrada1: instancia capa sobre la que se selecciona
    capa_entrada2: intancia segundo capara que participa en la seleccion
    predicado: Condicion espacial de seleccion
        0 — intersecta
        1 — contiene
        2 — dividir
        3 — igual
        4 — toca
        5 — superpone
        6 — esta dentro
        7 — cruza
    """
    
    parameter = {"INPUT": capa_entrada1, "PREDICATE": predicado,
         "INTERSECT": capa_entrada2, "OUTPUT": "TEMPORARY_OUTPUT"}
    processing.run("qgis:selectbylocation", parameter)


# Funcion para hacer buffer
def buffer(capa_entrada, capa_salida, distancia):
    """
    Buffer de una capa vectorial
    Se exporta directamente como capa
    
    Argumentos:
    capa_entrada: instancia de la capa sobre la que se realiza el buffer
    capa_salida: nombre shp salida sin extension
    distancia: distancia en metros de buffer
    * Metros porque se ha proyectado a metros
    """
    
    output = capa_salida + ".shp"
    parameter = {"INPUT": capa_entrada,"DISTANCE": distancia,\
        "DISSOLVE": True, "OUTPUT": output}
    processing.run("qgis:buffer", parameter)
    

# Funcion para borrar archivos innecesarios
# Se borran los archivos generados (conservando los originales y el final)
# Se van borrando segun no se utilicen mas para optimizar la memoria
def borrar_innecesarios(capa):
    """
    Borra los shp y sus asociados no necesarios.
    Solo interesa quedarnos con el resultado final
    
    Argumentos:
    capa: nombre de la capa con extension que se
    desea eliminar del directorio
    """
    # Quitar la extension 
    nombre_capa = capa[:-4]
    
    capa_shx = nombre_capa + '.shx'
    capa_shp = nombre_capa + '.shp'
    capa_dbf = nombre_capa + '.dbf'
    capa_prj = nombre_capa + '.prj'
    capa_cpg = nombre_capa + '.cpg'
    
    lista_borrar = []
    lista_borrar.append(capa_shx)
    lista_borrar.append(capa_shp)
    lista_borrar.append(capa_dbf)
    lista_borrar.append(capa_prj)
    lista_borrar.append(capa_cpg)
    
    for elemento in lista_borrar:
        if os.path.exists(elemento):
            os.remove(elemento)

# Establecer espacio de trabajo
directorio = r"C:\Users\elena\Desktop\Universidad\MasterTIGUAH\Programacion\Trabajofinal\Materialpractica\capas_entrada"
os.chdir(directorio)

lista_archivos = os.listdir()  # Lista de las capas en el espacio de trabajo

# Abrir tambien el csv (tabla) separado por punto y comas
# Usamos esta forma para importar solo un dbf (no esta asociado a shp) y no todos

nombre_archivo_csv = "Brussels_AverageAge.csv"
uri = "file:///" + directorio + "\\" + nombre_archivo_csv + "?delimiter=;"
# El csv se instancia diferente
# Se carga como una tabla usado el proveedor delimitedtext
# Instancia
Brussels_AverageAge = QgsVectorLayer(uri, nombre_archivo_csv, "delimitedtext")

print ("*" * 20)
for archivo in lista_archivos:
    if archivo[-4:] == ".shp": # Quedarnos solo con los shp
        if archivo[:-5] == "repr_":
            # Para no meter en el bucle las capas reproyectadas creadas
            pass
        else:
            # Quitar la extension
            
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
                
                # Necesario decir que la capa de salida es shp (si no formato 
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
                    
                if proyeccion == "":
                    print ("{0} no tenía proyección y se ha creado {1} con {2}".\
                        format(archivo, nombre_capa_reproyectada_extension, proyeccion_final))
                
                else:
                    print ("De {0} con {1} se ha creado {2} con {3}".\
                        format(archivo, proyeccion, nombre_capa_reproyectada_extension, proyeccion_final))

            elif proyeccion == "EPSG:31370":
                # No hace falta hacer nada si ya tien el EPSG deseado
                pass
                
                print ("La capa {0} ya tenia el EPSG correcto ({1}). No se ha reproyectado."\
                .format(archivo, proyeccion))

# Se desinstancia porque luego cada instancia tiene diferente nombre
instancia = None

print ("*" * 20)

# Siguente paso: hacer joins
# 1. Entre capa densidad de poblacion y tabla
# 2. Entre el resultado del anterior join y Average_Income.shp
# Se deben instanciar diferenciadas las capas que participan en el join
# El csv ya se instancio arriba de forma diferente
shp1 = "repr_Population_Density.shp"
Population_Density = instanciar(shp1)
shp2 = "repr_Average_Income.shp"
Average_Income = instanciar(shp2)

# Campos para hacer los join
shpField="MUNC"
csvField="Munc"
# Hacer los joins (se concatenan y se alamacena todo en la misma capa)
join(Population_Density, Brussels_AverageAge, shpField, csvField)
join(Population_Density, Average_Income, shpField, shpField)

# Se puede observar como se han añadido nuevos campos de la tabla (ejemplo con join 1)
print ("Campos tras el join en {0}:".format(shp1))
for field in Population_Density.fields():
    print(field.name(), field.typeName())

# CREAR CAMPOS DE AREAS Y DENSIDAD DE POBLACION

# Campos que se desean crear
campo1 = "Area_km2"  # Area (km2)
campo2 = "Dens_pop"  # Densidad poblacion (hb/km2)
lista_campos = [campo1, campo2]

# Para verificar que no existe el campo. Si existe borrar
for campo in lista_campos:
    indice_borrar = indice_campo(Population_Density, campo)
    if indice_borrar != -1:
        Population_Density.startEditing()
        Population_Density.dataProvider().deleteAttributes([indice_borrar])
        Population_Density.commitChanges()

# Se crean los campos deseados
res_campo = Population_Density.dataProvider().addAttributes(
            [QgsField(campo1, QVariant.Double),
            QgsField(campo2, QVariant.Double)])

# Para comprobar si el campo se ha añadido o no
for campo in lista_campos:
    if res_campo == True:
        print('Campo "{0}" creado satisfactoriamente.'.format(campo))
    else:
        print('No se ha podido crear el campo.')

# Se actualian los campos del layer para que se carguen en el layer
Population_Density.updateFields()

features = Population_Density.getFeatures()

# Se crea lista de area y densidad para guardar los valores a cargar
areas = []
lista_densidad = []

# Se mira la geometria y se calcula para cada entidad los valores
for f in features:
    geom = f.geometry()
    area = geom.area() / 1000000
    areas.append(area)
    poblacion = f.attribute('F2010')
    densidad = poblacion / area
    lista_densidad.append(densidad)

# Numero entidades
numero = Population_Density.featureCount()

indice1 = indice_campo(Population_Density, "Area_km2")
indice2 = indice_campo(Population_Density, "Dens_pop")

# Comenzar la edicion
Population_Density.startEditing()

# Actualiar campos
for i in range(numero):
    Population_Density.changeAttributeValue(i, indice1, areas[i])
    Population_Density.changeAttributeValue(i, indice2, lista_densidad[i])
    
# Guardar cambios
Population_Density.commitChanges()


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

# Seleccion 2. Seleccion por expresion de caracteristicas de la poblacion
# del resultado del join
# Se usa and en vez de or porque se queiren las 3 condiciones a la vez
exp_selec_2 = "\"Dens_pop\" > 2000 and \"Brussels_AverageAge.csv_AverageAge\"\
    < 37 and \"repr_Average_Income.shp_I_hab_10\" > 10000"
Population_Density.selectByExpression(exp_selec_2, QgsVectorLayer.SetSelection)
shp_salida = "muni_select"
exportar(Population_Density, shp_salida)

# Seleccion 3. Seleccion por expresion de condiciones de la ciudad Bruselas
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
selec_localizacion(land_select, muni_select, 6)
shp_salida = "land_muni_select"
exportar(land_select, shp_salida)
"""
                        muni_select = ""
                        borrar_innecesarios(shp4)
                        land_select = ""
                        borrar_innecesarios(shp5)
"""
# Buffer de 499.999 m desde RoadRailways
# Se usa algortimo de procesameinto: qgis.buffer
shp6 = "RoadRailways.shp"  # Instancio
RoadRailways = instanciar(shp6)
buffer(RoadRailways, "buffer_carreteras", 499.999)
"""
                        RoadRailways = ""
                        borrar_innecesarios(shp6)
"""
# Seleccion 5. Seleccion por localizacion
# Seleccionar parcelas de land_muni_select a menos de 500 m de carreteras
# (usando el buffer)
shp7 = "buffer_carreteras.shp"
buffer_carreteras = instanciar(shp7)
shp8= "land_muni_select.shp"
land_muni_select = instanciar(shp8)
selec_localizacion(land_muni_select, buffer_carreteras, 0)
# Como en verdad se quiere seleccionar las que quedan a mas
# de 500 m se debe hacer el inverso de esta seleccion
land_muni_select.invertSelection()
shp_salida = "Parcels_dist_transport"
exportar(land_muni_select, shp_salida)
"""
                        buffer_carreteras = ""
                        borrar_innecesarios(shp7)
                        land_muni_select = ""
                        borrar_innecesarios(shp8)
"""
# Seleccion 6. Seleccion por localizacion
# Seleccion de zoas a menos de 500 m de escuelas primarias
# menos de 500 m = 499.999 m
# Necesario hacer un buffer como antes
shp9 = "repr_Primary_schools.shp"
Primary_schools = instanciar(shp9)
# Creacion del buffer
buffer(Primary_schools, "buffer_escuelas_primaria", 499.999)
# Seleccion por localizacion
shp10 = "Parcels_dist_transport.shp"
Parcels_dist_transport = instanciar(shp10)
shp11 = "buffer_escuelas_primaria.shp"
buffer_escuelas_primaria = instanciar(shp11)
selec_localizacion(Parcels_dist_transport, buffer_escuelas_primaria, 0)
shp_salida = "Selec_final"
exportar(Parcels_dist_transport, shp_salida)

"""
                            Population_Density = ""
                            borrar_innecesarios(shp1)
                            Average_Income = ""
                            borrar_innecesarios(shp2)
                            Primary_schools = ""
                            borrar_innecesarios(shp9)
                            Parcels_dist_transport = ""
                            borrar_innecesarios(shp10)
                            buffer_escuelas_primaria = ""
                            borrar_innecesarios(shp11)
"""
