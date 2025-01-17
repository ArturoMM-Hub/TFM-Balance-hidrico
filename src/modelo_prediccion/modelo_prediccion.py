from prophet import Prophet
import matplotlib.pyplot as plt
from  config.constantes import RUTA_BASE_FICHEROS_PROCESADOS
import os
import pandas as pd


 
def modelo_prediccion():
    print("Inicio generando modelo prediccion")
    # Obtencion de los archivos
    archivos_y_directorios = os.listdir(RUTA_BASE_FICHEROS_PROCESADOS)
    archivos = [f for f in archivos_y_directorios if os.path.isfile(os.path.join(RUTA_BASE_FICHEROS_PROCESADOS, f))]

    for estacion_meteorologica_file in archivos:

        estacion_data = pd.read_json(RUTA_BASE_FICHEROS_PROCESADOS + estacion_meteorologica_file)
        # Preparo los datos para Prophet
        estacion_data = estacion_data.reset_index()[['fecha', 'sequia_meteorologica']]
        estacion_data.columns = ['ds', 'y']  # Prophet requiere columnas 'ds' (fecha) y 'y' (valor)

        # Creo y entreno el modelo Prophet
        modelo_prophet = Prophet()
        modelo_prophet.fit(estacion_data)

        # Genero futuro y las predicciones
        future = modelo_prophet.make_future_dataframe(periods=12, freq='M')  # Predice 12 meses adicionales
        forecast = modelo_prophet.predict(future)

        # Lo muestro
        modelo_prophet.plot(forecast)
        plt.title('Predicción de sequía con Prophet')
        plt.show()
    
    print("Fin modelo prediccion generado")
