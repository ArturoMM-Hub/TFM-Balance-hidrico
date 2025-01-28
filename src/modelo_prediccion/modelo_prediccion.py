from prophet import Prophet
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') # Le quito el entorno interactivo para uqe no muestre todo el rato una ventana de grafico
from  config.constantes import RUTA_BASE_FICHEROS_PROCESADOS, RUTA_BASE_RESULTADOS_PREDICCIONES, YEAR_OF_PREDICTION, ARCHIVO_ESTACIONES_METEOROLOGICAS, NOMBRE_ARCHIVO_RESULTADO_PREDICCION
import os
import pandas as pd
import json
from transform.main_transformacion import corregir_valores_rango_uno_cero, set_datos_estaciones


def get_prediccion_prohet(estacion_data, nomb_columna_a_predecire, estacion_meteorologica_file):
    try:
        meteorologica_data  = estacion_data.dropna(subset=['fecha', nomb_columna_a_predecire])
        meteorologica_data  = meteorologica_data[['fecha', nomb_columna_a_predecire]].rename(columns={'fecha': 'ds', nomb_columna_a_predecire: 'y'})
        meteorologica_data  = meteorologica_data .set_index('ds').resample('M').mean().reset_index()

        # Configuro y entreno modelo
        modelo_prophet_meteorologica = Prophet(yearly_seasonality=True, interval_width=0.95)
        modelo_prophet_meteorologica.fit(meteorologica_data)

        # Predicciones
        future_meteorologica  = modelo_prophet_meteorologica.make_future_dataframe(periods=12 * YEAR_OF_PREDICTION, freq='M')
        forecast_meteorologica  = modelo_prophet_meteorologica.predict(future_meteorologica)

        # Filtro solo las nuevas fechas predichas
        output = forecast_meteorologica[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
        nuevas_fechas_meteorologica = output[output['ds'] > estacion_data['fecha'].max()]
        nuevas_fechas_meteorologica = nuevas_fechas_meteorologica[['ds', 'yhat']].rename(columns={'ds': 'fecha', 'yhat': nomb_columna_a_predecire})
        
        # Corrijo valores por debajo de 0
        nuevas_fechas_meteorologica = corregir_valores_rango_uno_cero(nuevas_fechas_meteorologica , nomb_columna_a_predecire)

        forecast_meteorologica = corregir_valores_rango_uno_cero(forecast_meteorologica , 'yhat')

        # Guardar gráfico en PNG
        fig = modelo_prophet_meteorologica.plot(forecast_meteorologica)
        fig.savefig(RUTA_BASE_RESULTADOS_PREDICCIONES + estacion_meteorologica_file + "-" + nomb_columna_a_predecire +"-prediccion-grafico.png")
        
    except Exception as e:
        print(e)
    return nuevas_fechas_meteorologica
 
def modelo_prediccion():
    print("Inicio generando modelo prediccion")
    df_global_toda_espania = pd.DataFrame()
    # Obtencion de los archivos
    #Estacion meteorologica
    with open(ARCHIVO_ESTACIONES_METEOROLOGICAS, 'r', encoding='utf-8') as file:
        estacionesObj = json.load(file)

    # Archivos de la carpeta de procesados para hacer la prediccion a futuro
    archivos = [f for f in os.listdir(RUTA_BASE_FICHEROS_PROCESADOS) if os.path.isfile(os.path.join(RUTA_BASE_FICHEROS_PROCESADOS, f))]

    for estacion_meteorologica_file in archivos:
        try:
            estacion_data = pd.read_json(RUTA_BASE_FICHEROS_PROCESADOS + estacion_meteorologica_file)

            # Preparo los datos ya que la fecha tiene que estar en Datetime para que funcione
            estacion_data['fecha'] = pd.to_datetime(estacion_data['fecha'], errors='coerce')

        # SEQUIA METEOROLOGICA
            nuevas_fechas_meteo = get_prediccion_prohet(estacion_data, 'sequia_meteorologica', estacion_meteorologica_file.replace(".json", ""))
        
        # SEQUIA AGRICOLA
            nuevas_fechas_agricola = get_prediccion_prohet(estacion_data, 'sequia_agricola', estacion_meteorologica_file.replace(".json", ""))

            # Saco factor comun para tener por cada fecha las dos sequias
            nuevas_fechas_combinadas = pd.merge(nuevas_fechas_meteo, nuevas_fechas_agricola, on='fecha', how='inner') # Como tienen las mismas fechas las combino

            # Les pongo a los valores datos de sus respectivas estaciones
            nuevas_fechas_combinadas = set_datos_estaciones(nuevas_fechas_combinadas, estacionesObj, estacion_meteorologica_file.replace(".json", ""))

            # Agrego las nuevas fechas predichas al DataFrame original 'estacion_data'
            estacion_data = pd.concat([estacion_data, nuevas_fechas_combinadas], ignore_index=True)


            # Ordeno por fecha ya que esta todo unido en esa estacion meteorologica
            estacion_data = estacion_data.sort_values('fecha')

            # Agrego al Dataframe al global para tener todos los registros de espania
            df_global_toda_espania = pd.concat([df_global_toda_espania, estacion_data], ignore_index=True)
        
        except Exception as e:
            print(f"Error al procesar {estacion_meteorologica_file}: {e}")
    
    # Guardo todos los datos del dataframe en un json
    df_global_toda_espania.to_json(RUTA_BASE_RESULTADOS_PREDICCIONES + NOMBRE_ARCHIVO_RESULTADO_PREDICCION, 
                                    orient="records", date_format="iso", indent=4)

    print("Fin modelo prediccion generado")
