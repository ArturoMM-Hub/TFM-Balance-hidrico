from  config.constantes import RUTA_BASE_FICHEROS_RAW, ARCHIVO_ESTACIONES_METEOROLOGICAS
import http.client
import json
import requests
import os
import sys

class AemetWriter:

    @staticmethod
    def guardar_en_json(year, provincia, estacion_meteorologica, prediccion_meteorologica):
        
        #Creo la ruta si no esxiste
        ruta = RUTA_BASE_FICHEROS_RAW + year + "/"
        if not os.path.exists(ruta):
            os.makedirs(ruta)

        if isinstance(prediccion_meteorologica, bytes):
            prediccion_meteorologica = prediccion_meteorologica.decode('utf-8')
        
        def decode_bytes(obj):
            if isinstance(obj, bytes):
                return obj.decode('utf-8')
            elif isinstance(obj, dict):
                return {k: decode_bytes(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [decode_bytes(i) for i in obj]
            return obj
        
        prediccion_meteorologica = decode_bytes(prediccion_meteorologica)

        # Guarda los datos en un archivo
        nombre_archivo = AemetWriter.get_file_name(year, provincia, estacion_meteorologica["indicativo"], estacion_meteorologica["nombre"])
        print(nombre_archivo)
        with open(ruta + nombre_archivo, "w", encoding="utf-8") as file:
            json.dump(prediccion_meteorologica, file, indent=4, ensure_ascii=False)

    
    def get_file_name(year, provincia, id_estacion_meteorologica, nombre_estacion_meteorologica):
        nombre_archivo_salida = provincia + "-" + str(id_estacion_meteorologica) + "-" + str(nombre_estacion_meteorologica) + "-" + str(year) + ".json" # Nombre del archivo
        nombre_archivo_salida = nombre_archivo_salida.replace(",", "_").replace("/", "_").replace(" ", "_")
        return nombre_archivo_salida
    
    def guardarEstaciones(datos):
        with open(ARCHIVO_ESTACIONES_METEOROLOGICAS, "w", encoding="utf-8") as file:
            json.dump(datos, file, indent=4, ensure_ascii=False)