import http.client
import json
import requests
from  config.constantes import URL_AEMET, API_KEY_AEMET

class AemetReader:

    token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhcnR1cm8ubXVub3oubWFydGluZXoxNEBnbWFpbC5jb20iLCJqdGkiOiIyNTQ5OGQ2MS1iYzQ2LTRjYTgtYWQ1ZC1mZDY0YjJhYWRkMGMiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTczNTU5ODQ5OSwidXNlcklkIjoiMjU0OThkNjEtYmM0Ni00Y2E4LWFkNWQtZmQ2NGIyYWFkZDBjIiwicm9sZSI6IiJ9.hnhiQD0dE5xlbIymauJuXjis0UFs_JfhC1gNfJWuaUo"

    @staticmethod
    def getPredicionTiempo(year, cod_estacion):
        conn = http.client.HTTPSConnection(URL_AEMET)

        headers = {
            'cache-control': "no-cache"
        }

        # Primera solicitud a la API
        conn.request("GET", f"/opendata/api/valores/climatologicos/mensualesanuales/datos/anioini/{year}/aniofin/{year}/estacion/{cod_estacion}/?api_key={API_KEY_AEMET}", headers=headers)
        res = conn.getresponse()
        data = res.read()

        try:
            # Intentar decodificar como UTF-8
            response_json = json.loads(data.decode("utf-8"))
        except UnicodeDecodeError:
            # Si falla, usar ISO-8859-1
            response_json = json.loads(data.decode("ISO-8859-1"))

        # Verificar el estado de la respuesta
        if response_json.get("estado") == 200:
            # Extraer la URL de datos
            datos_url = response_json.get("datos")

            # Hacer una segunda solicitud a la URL de datos
            conn.request("GET", datos_url, headers=headers)
            datos_res = conn.getresponse()
            datos_bytes = datos_res.read()

            try:
                datos_decoded = datos_bytes.decode("utf-8")
            except UnicodeDecodeError:
                datos_decoded = datos_bytes.decode("ISO-8859-1")

            # **Depuración: Verificar el contenido de datos_decoded**
            #print(f"Contenido de datos_decoded:\n{datos_decoded[:500]}")  # Limitar la salida a los primeros 500 caracteres

            if not datos_decoded.strip():
                print("Error: La respuesta de la API está vacía.")
                return {}

            try:
                # Intentar cargar los datos como JSON
                return json.loads(datos_decoded)
            except json.JSONDecodeError as e:
                print(f"Error al decodificar JSON: {e}")
                print(f"Contenido que falló:\n{datos_decoded}")
                return {}
        elif response_json.get("estado") == 429: # limite de las solicitudes obtenido
            print(f"Error en la solicitud inicial: limite de las solicitudes obtenido")
            return { 
                'estado' : response_json.get('estado'),
                'error' : response_json.get('descripcion')}
        else:
            print(f"Error en la solicitud inicial: {response_json.get('descripcion')}")
            return {}



    def getEstacionesMeteorologicas():

        estaciones = AemetReader.getResponse("/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones")

        if type(estaciones) != str:# si es str es porque devuelcvo un error

            #Formateo un objeto que por cada provincia meta sus estaciones
            estaciones_por_provincia = {}

            for estacion in estaciones:
                provincia = estacion.get("provincia", "Desconocida")  # Obtener la provincia
                if provincia not in estaciones_por_provincia:
                    estaciones_por_provincia[provincia] = []  # Inicializar lista si no existe
                estaciones_por_provincia[provincia].append(estacion)  # Agregar la estación a la lista

            
        #print(json.dumps(estaciones_por_provincia, indent=2, ensure_ascii=False))
        return estaciones_por_provincia
    

    def getResponse(url):
        datos = ""
        conn = http.client.HTTPSConnection(URL_AEMET)

        headers = {
            'cache-control': "no-cache"
        }

        try:
            # Primera solicitud a la API
            conn.request("GET", url+f"/?api_key={API_KEY_AEMET}", headers=headers)
            res = conn.getresponse()
            data = res.read()
            response_json = json.loads(data.decode("utf-8"))  # Parsear la respuesta JSON

            # Verificar el estado
            if response_json.get("estado") == 200:
                # Extraer la URL de "datos"
                datos_url = response_json.get("datos")

                # Hacer una segunda solicitud a la URL de datos
                conn.request("GET", datos_url, headers=headers)
                datos_res = conn.getresponse()
                lecturabytes = datos_res.read()

                #decodifico a mi lenguaje
                datos_decoded = ""
                try:
                    datos_decoded = lecturabytes.decode('ISO-8859-1')
                    datos = json.loads(datos_decoded)
                except UnicodeDecodeError as e:
                    print(f"Error al decodificar datos: {e} {url}")
                    datos_decoded = json.loads(lecturabytes.decode("utf-8"))
                    

                

            else:
                print(f"Error en la solicitud: {response_json.get('descripcion')}")
        except json.JSONDecodeError as e:
            print(f"Error al parsear JSON: {e}")
       
        except Exception as e:
            print(f"Error general: {e}")
        finally:
            conn.close()
        return datos