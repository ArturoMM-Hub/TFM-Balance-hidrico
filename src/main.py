from extract.MainExtract import mainExtract
from transform.main_transformacion import mainTransform
import time
import os

def main():
    print("Inicio flujo")

    # Extract: Saco los datos de Aemet y los guarda en json en la ruta 'resources/raw/'
    #mainExtract()

    # Transform: limpieza del dato y agrupacion de datos
    mainTransform()


    
    print("Fin flujo")
    pass


if __name__ == '__main__':
    main()