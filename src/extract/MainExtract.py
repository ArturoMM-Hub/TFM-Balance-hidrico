from extract.reader.aemet_reader import AemetReader
from extract.writer.aemet_writer import AemetWriter
from  config.constantes import RUTA_BASE_FICHEROS_RAW, ARCHIVO_INDICE_SOLAR, YEAR_INICIO_OBTENCION_VALORES, YEAR_FIN_OBTENCION_VALORES
import time
import os

def getYearWeather(year, provincia, estacion_meteorologica,cont):
    try:
        nombre_archivo = AemetWriter.get_file_name(year, provincia, estacion_meteorologica["indicativo"], estacion_meteorologica["nombre"])
        if os.path.exists(RUTA_BASE_FICHEROS_RAW + str(year) + "/" + nombre_archivo) == False:
            cont += 1 
            print(str(cont) + " " + provincia + " " + estacion_meteorologica["indicativo"])
            if cont == 19:
                time.sleep(60)#pongo a dormir para que la api no me rechaze tantas peticiones
                cont = 0
            datos = AemetReader.getPredicionTiempo(year, estacion_meteorologica["indicativo"])

            if datos != {}:
                if  isinstance(datos, list) and 'estado' not in datos: # Si esta aqui no tiene un error, solo devuelvo estado si tiene un error
                    AemetWriter.guardar_en_json(year,provincia ,estacion_meteorologica, datos) 
                else:
                    time.sleep(90)
                    getYearWeather(year, provincia, estacion_meteorologica) # Lo vuelvo a llamar
        else:
            print("ya existia " + nombre_archivo)
    except Exception as ex:
        return ex

def mainExtract():
    print("Inicio flujo Extracción")
    estaciones_por_provincias = AemetReader.getEstacionesMeteorologicas()
    #Guardo las estaciones en un json
    if os.path.exists(ARCHIVO_INDICE_SOLAR) == False:
        AemetWriter.guardarEstaciones(estaciones_por_provincias)

    cont= 1
    for year in range(YEAR_INICIO_OBTENCION_VALORES, YEAR_FIN_OBTENCION_VALORES):
        print(year)
        for provincia in estaciones_por_provincias:

            for estacion_meteorologica in estaciones_por_provincias[provincia]:
                getYearWeather(year, provincia, estacion_meteorologica, cont)                    

    print("Fin flujo Extracción")
    return True
