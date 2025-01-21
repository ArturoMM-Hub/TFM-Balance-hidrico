# constantes.py

# Directorios
RUTA_BASE_FICHEROS_RAW = "resources/raw/"
RUTA_BASE_FICHEROS_PROCESADOS = "resources/processed/"
RUTA_BASE_LOGS = "resources/logs/"
RUTA_BASE_RESULTADOS_PREDICCIONES = "resources/resultados_predicciones/"
ARCHIVO_INDICE_SOLAR = "resources/indice_solar.json"
ARCHIVO_ESTACIONES_METEOROLOGICAS = "resources/estaciones_meteorologicas.json"

# API
URL_AEMET = "https://opendata.aemet.es/opendata/api"
API_KEY = "tu_api_key_aemet"

# Otros valores
MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

INDICE_SOLAR = {
    "Enero": 0.3,
    "Febrero": 0.4,
    "Marzo": 0.5,
    "Abril": 0.6,
    "Mayo": 0.7,
    "Junio": 0.9,
    "Julio": 1.0,
    "Agosto": 0.9,
    "Septiembre": 0.7,
    "Octubre": 0.5,
    "Noviembre": 0.3,
    "Diciembre": 0.2
}

YEAR_OF_PREDICTION = 3 # 3 años 

# Aumento de temperatura por año en ºC
AUMENTO_TEMPERATURA_CAMBIO_CLIMATICO = 0.03
