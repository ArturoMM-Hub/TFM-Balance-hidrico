from prophet import Prophet
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') # Le quito el entorno interactivo para uqe no muestre todo el rato una ventana de grafico
from  config.constantes import RUTA_BASE_FICHEROS_PROCESADOS, RUTA_BASE_RESULTADOS_PREDICCIONES, YEAR_OF_PREDICTION
import os
import pandas as pd
from transform.main_transformacion import corregir_valores_rango_uno_cero


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
        #nuevas_fechas_meteorologica = corregir_valores_rango_uno_cero(nuevas_fechas_meteorologica , nomb_columna_a_predecire)

        '''
        output = forecast_meteorologica[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
        output.to_json(RUTA_BASE_RESULTADOS_PREDICCIONES + estacion_meteorologica_file + "_predicciones_sequia.json", orient="records", date_format="iso", indent=4)
'''
        # Guardar gráfico en PNG
        fig = modelo_prophet_meteorologica.plot(forecast_meteorologica )
        fig.savefig(RUTA_BASE_RESULTADOS_PREDICCIONES + estacion_meteorologica_file + nomb_columna_a_predecire +"_prediccion_prophet.png")
        
    except Exception as e:
        print(e)
    return nuevas_fechas_meteorologica
 
def modelo_prediccion():
    print("Inicio generando modelo prediccion")
    # Obtencion de los archivos
    archivos = [f for f in os.listdir(RUTA_BASE_FICHEROS_PROCESADOS) if os.path.isfile(os.path.join(RUTA_BASE_FICHEROS_PROCESADOS, f))]

    for estacion_meteorologica_file in archivos:
        try:
            estacion_data = pd.read_json(RUTA_BASE_FICHEROS_PROCESADOS + estacion_meteorologica_file)

            # Preparo los datos ya que la fecha tiene que estar en Datetime para que funcione
            estacion_data['fecha'] = pd.to_datetime(estacion_data['fecha'], errors='coerce')

        # SEQUIA METEOROLOGICA
            nuevas_fechas_meteo = get_prediccion_prohet(estacion_data, 'sequia_meteorologica', estacion_meteorologica_file)
        
        # SEQUIA AGRICOLA
            nuevas_fechas_agricola = get_prediccion_prohet(estacion_data, 'sequia_agricola', estacion_meteorologica_file)


            nuevas_fechas_combinadas = pd.merge(nuevas_fechas_meteo, nuevas_fechas_agricola, on='fecha', how='inner') # Como tienen las mismas fechas las combino
            # Correccion de valores nuevas_fechas_combinadas
            

            # Agrego las nuevas fechas predichas al DataFrame original 'estacion_data'
            estacion_data = pd.concat([estacion_data, nuevas_fechas_combinadas], ignore_index=True)


            # Guardar el DataFrame actualizado
            # print(estacion_data)
            estacion_data = estacion_data.sort_values('fecha')
            estacion_data.to_json(RUTA_BASE_RESULTADOS_PREDICCIONES + estacion_meteorologica_file + "_predicciones_actualizadas.json", 
                                    orient="records", date_format="iso", indent=4)
        except Exception as e:
            print(f"Error al procesar {estacion_meteorologica_file}: {e}")

    print("Fin modelo prediccion generado")
