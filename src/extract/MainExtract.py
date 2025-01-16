from extract.reader.aemet_reader import AemetReader
from extract.writer.aemet_writer import AemetWriter
from  config.constantes import RUTA_BASE_FICHEROS_RAW, ARCHIVO_ESTACIONES_METEOROLOGICAS
import time
import os

def mainExtract():
    print("Inicio flujo Extracción")
    estaciones_por_provincias = AemetReader.getEstacionesMeteorologicas()
    #Guardo las estaciones en un json
    if os.path.exists(ARCHIVO_ESTACIONES_METEOROLOGICAS) == False:
        AemetWriter.guardarEstaciones(estaciones_por_provincias)

    cont= 1
    for year in range(2021, 2025):
        print(year)
        for provincia in estaciones_por_provincias:

            for estacion_meteorologica in estaciones_por_provincias[provincia]:
                nombre_archivo = AemetWriter.get_file_name(year, provincia, estacion_meteorologica["indicativo"], estacion_meteorologica["nombre"])
                if os.path.exists(RUTA_BASE_FICHEROS_RAW + year + "/" + nombre_archivo) == False:
                    cont += 1 
                    print(str(cont) + " " + provincia + " " + estacion_meteorologica["indicativo"])
                    if cont == 19:
                        time.sleep(60)#pongo a dormir para que la api no me rechaze tantas peticiones
                        cont = 0
                    datos = AemetReader.getPredicionTiempo(year, estacion_meteorologica["indicativo"])

                    if datos != {}:
                        AemetWriter.guardar_en_json(year,provincia ,estacion_meteorologica, datos) 
                else:
                    print("ya existia " + nombre_archivo)
    print("Fin flujo Extracción")
    return True
