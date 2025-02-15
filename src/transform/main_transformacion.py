import pandas as pd
import numpy as np
import json
import os
import re
from datetime import datetime
from  config.constantes import RUTA_BASE_FICHEROS_RAW, INDICE_SOLAR, AUMENTO_TEMPERATURA_CAMBIO_CLIMATICO, RUTA_BASE_FICHEROS_PROCESADOS, RUTA_BASE_LOGS, ARCHIVO_ESTACIONES_METEOROLOGICAS



def guardarEnJSON(estacion_meteorologica_file, df_datos_a_insertar):
    datos_nombre_archivo = estacion_meteorologica_file.split('-')
    existe = False
    # datos_nombre_archivo[2] es el codigo de la estacion
    if datos_nombre_archivo[1] != None:
        # Como aqui no hay mas carpetas directamente esto me devuelve los ficheros
        archivos = os.listdir(RUTA_BASE_FICHEROS_PROCESADOS)
        for nomb_file in archivos:
            if datos_nombre_archivo[2] in nomb_file:
                df_datos_existente = pd.read_json(RUTA_BASE_FICHEROS_PROCESADOS + nomb_file)
                df_final = pd.concat([df_datos_existente, df_datos_a_insertar], ignore_index=True)
                existe = True
                break
        
        nombFile = datos_nombre_archivo[0] + "-" + datos_nombre_archivo[1] + "-" + datos_nombre_archivo[2] + ".json"
        if existe: 
            # Guardo la combinacion del que ya habia y el nuevo
            df_final.to_json(RUTA_BASE_FICHEROS_PROCESADOS + nombFile, 
                                     orient="records", 
                                     force_ascii=False,
                                     indent=4)
        else:
            # Creo del archivo por primera vez si no existia pra esa estacion
            df_datos_a_insertar.to_json(RUTA_BASE_FICHEROS_PROCESADOS + nombFile, 
                                     orient="records", 
                                     force_ascii=False,
                                     indent=4)


def buscar_por_indicativo_la_estacion(data, indicativo):
    for provincia, estaciones in data.items():
        for estacion in estaciones:
            if estacion.get("indicativo") == indicativo:
                return estacion
    return None


def corregir_valores_rango_uno_cero(dataframe, nombColumna):
    dataframe[nombColumna] = dataframe[nombColumna].apply(
                lambda x: 0.5 if pd.isna(x) else max(0, min(x, 1))
            )
    return dataframe


def convertir_a_decimal_coordenadas(coordenada):
    # Extraigo grados, minutos, segundos y dirección
    match = re.match(r"(\d{2,3})(\d{2})(\d{2})([NSEW])", coordenada)
    if not match:
        raise ValueError(f"Formato inválido: {coordenada}")
    
    grados = int(match.group(1))
    minutos = int(match.group(2))
    segundos = int(match.group(3))
    direccion = match.group(4)

    # Convertir a decimal
    decimal = grados + (minutos / 60) + (segundos / 3600)
    
    # Ajustar signo según la dirección
    if direccion in ['S', 'W']:
        decimal = -decimal

    return decimal

def set_datos_estaciones(df_final, estacionesObj, estacion_meteorologica_file):
    nomb_file = estacion_meteorologica_file.replace(".json", "")
    datos_estacion = buscar_por_indicativo_la_estacion(estacionesObj, nomb_file.split('-')[1]) # estacion_meteorologica_file.split('-')[1] es el codigo indicativo
    if datos_estacion == None: # Porque alguna provincia viene con el '-', por ejemplo Araba-Alaba
        datos_estacion = buscar_por_indicativo_la_estacion(estacionesObj, nomb_file.split('-')[2])
    df_final["nomb_estacion"] = datos_estacion["nombre"]
    df_final["provincia"] = datos_estacion["provincia"]
    df_final["lat"] = convertir_a_decimal_coordenadas(datos_estacion["latitud"]) # convierto las cordenadas a decimal porque en porwer BI
    df_final["long"] = convertir_a_decimal_coordenadas(datos_estacion["longitud"])

    return df_final


def mainTransform():
    print("Inicio flujo Tranformacion")
    # Filtro por las carpetas
    with open(ARCHIVO_ESTACIONES_METEOROLOGICAS, 'r', encoding='utf-8') as file:
        estacionesObj = json.load(file)

    carpetas = [f for f in os.listdir(RUTA_BASE_FICHEROS_RAW) if os.path.isdir(os.path.join(RUTA_BASE_FICHEROS_RAW, f))]
    indice_solar_dict = INDICE_SOLAR

    rutalog = RUTA_BASE_LOGS + 'log' + str(datetime.now().year) + "-" + str(datetime.now().month) + "-" + str(datetime.now().day) + '.txt'


    for dir in carpetas:
        # Obtencion de los archivos
        ruta_archivos = RUTA_BASE_FICHEROS_RAW + dir + "/"
        archivos_y_directorios = os.listdir(ruta_archivos)
        archivos = [f for f in archivos_y_directorios if os.path.isfile(os.path.join(ruta_archivos, f))]
        
        for estacion_meteorologica_file in archivos:
            print(estacion_meteorologica_file)
            df_datos_estaciones = pd.read_json(ruta_archivos + estacion_meteorologica_file)
            cumple_requisitos = True

            try:
                columnas_necesarias = ['indicativo', 'fecha', 'p_max', 'tm_min', 'tm_max', 'ta_max', 'ta_min', 'ts_min', 'ti_max',
                                        'np_001', 'np_010', 'np_100', 'np_300', 'e', 'p_mes', 'nt_00', 'tm_mes'] 
                df_filtrado = df_datos_estaciones[columnas_necesarias]
                nombres_nuevos = {
                    'indicativo': 'id_estacion',
                    'fecha': 'fecha',
                    'p_max': 'precipitacion_maxima',
                    'tm_min': 'temperatura_media_minima_mensual', 
                    'ta_max': 'temperatura_max_absoluta_mes', 
                    'ts_min': 'temperatura_minima_mas_baja', 
                    'np_100': 'dias_con_precipitacion_mayor_10', 
                    'np_001': 'dias_con_precipitacion_mayor_01', 
                    'ta_min': 'temperatura_min_absoluta_mes', 
                    'e': 'tension_vapor_media', 
                    'np_300': 'dias_con_precipitacion_mayor_30', 
                    'p_mes': 'precipitacion_total_mes', 
                    'nt_00': 'dias_temperatura_menor_0', 
                    'ti_max': 'tempetatura_mas_baja_mes', 
                    'tm_mes': 'temperatura_media_mes', 
                    'tm_max': 'temperatura_media_maxima_mensual', 
                    'np_010': 'dias_con_precipitacion_mayor_0100'
                }
            except KeyError:
                # Si falla dejo los imprescindibles
                try:
                    columnas_necesarias = ['indicativo', 'fecha', 'tm_min', 'ti_max', 'p_mes', 'tm_mes'] 
                    df_filtrado = df_datos_estaciones[columnas_necesarias]
                    nombres_nuevos = {
                        'indicativo': 'id_estacion',
                        'fecha': 'fecha',
                        'tm_min': 'temperatura_media_minima_mensual', 
                        'p_mes': 'precipitacion_total_mes', 
                        'ti_max': 'tempetatura_mas_baja_mes', 
                        'tm_mes': 'temperatura_media_mes'
                    }
                except KeyError as e:
                    #Guardo en un log los archivos no aptos ni con los requerimientos básicos
                    with open(rutalog, "a", encoding="utf-8") as file:
                        file.write(estacion_meteorologica_file + f" No se pudo insertar por: '{e.args[0]}' \n")

            if cumple_requisitos:

                df_final = df_filtrado[~df_filtrado['fecha'].str.endswith("-13")]  # Filtro registros que no sean del mes 13
                
                # Renombro los campos
                df_final.rename(columns=nombres_nuevos, inplace=True)


            # Evaporacion (valores entre 1 y 0)
                # Evito divisiones por cero sumando un pequeño valor (epsilon) si la precipitación es 0
                epsilon = 1e-5
                df_aux = {}
                df_aux['indice_evaporacion'] = df_final['temperatura_media_mes'] / (
                    df_final['temperatura_media_mes'] + df_final['precipitacion_total_mes'] + epsilon
                )

                # Normalizo entre 0 y 1 
                df_final['indice_evaporacion'] = (df_aux['indice_evaporacion'] - df_aux['indice_evaporacion'].min()) / (
                    df_aux['indice_evaporacion'].max() - df_aux['indice_evaporacion'].min())

            #FECHA 
                # Normalizar el formato de la columna 'fecha'
                df_final['fecha'] = df_final['fecha'].str.replace(r"-(\d)$", r"-0\1", regex=True)
                # Convertir a formato datetime
                df_final['fecha'] = pd.to_datetime(df_final['fecha'], format='%Y-%m')
                df_final['mes'] = df_final['fecha'].dt.month # Extraigo el mes
                df_final['year'] = df_final['fecha'].dt.year
                
                # Formateo a str la fecha para que se vea bien en el json
                df_final['fecha'] = pd.to_datetime(df_final['fecha']).dt.strftime('%Y-%m-%d')
            # Indice Solar
                mes_a_indice_solar = {
                    1: indice_solar_dict["Enero"],
                    2: indice_solar_dict["Febrero"],
                    3: indice_solar_dict["Marzo"],
                    4: indice_solar_dict["Abril"],
                    5: indice_solar_dict["Mayo"],
                    6: indice_solar_dict["Junio"],
                    7: indice_solar_dict["Julio"],
                    8: indice_solar_dict["Agosto"],
                    9: indice_solar_dict["Septiembre"],
                    10: indice_solar_dict["Octubre"],
                    11: indice_solar_dict["Noviembre"],
                    12: indice_solar_dict["Diciembre"]
                }

                # Crear la columna 'indice_solar' mapeando los valores
                df_final['indice_solar'] = df_final['mes'].map(mes_a_indice_solar)

            # Sequia Meteorologica
                # Saco la media de los 12 meses con la funcion mean
                df_media_precipitaicones = df_final['precipitacion_total_mes'] - df_final['precipitacion_total_mes'].mean()
                df_final['sequia_meteorologica'] = (df_final['precipitacion_total_mes'] - df_final['precipitacion_total_mes'].mean()) / 100 # Saco el valor en porcentaje
                
                # Si hay valores por debajo de 0 es que no tienen sequia, los corrijo 0 y si hay nulos los pongo a 0.5
                df_final = corregir_valores_rango_uno_cero(df_final, 'sequia_meteorologica')
                
            # Sequia Agricola
                df_final['sequia_agricola'] = (df_media_precipitaicones - df_final['indice_solar'] - df_final['indice_evaporacion'] + AUMENTO_TEMPERATURA_CAMBIO_CLIMATICO) / 100 # Saco el valor en porcentaje tambien

                # Corrijo a 0 si hay algun negativo
                df_final = corregir_valores_rango_uno_cero(df_final, 'sequia_agricola')

            # Ordeno por mes, agrego datos de la estacion y Guardo los datos
                df_final = df_final.sort_values(by='mes', ascending=True)

                # Pongo datos de las estaciones
                df_final = set_datos_estaciones(df_final, estacionesObj, estacion_meteorologica_file)
                

                guardarEnJSON(estacion_meteorologica_file ,df_final)
                
         
    print("Fin flujo Transformacion")
    return True


