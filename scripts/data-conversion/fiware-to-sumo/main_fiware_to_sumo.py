import sys
from functions_fiware_to_sumo import *

def main():

    # Establecer la posición de la orden en la línea de argumentos
    orden = sys.argv[1]

    if orden == "FIWARE_to_SUMO":
        originalFIWAREroute = sys.argv[2]
        originalSUMOline = sys.argv[3]
        convert_FIWARE_route_to_SUMO_line(originalFIWAREroute, originalSUMOline)
    #python main_fiware_to_sumo.py FIWARE_to_SUMO originalFIWAREroute.json prueba.xml

    else:
        print(f"Orden no reconocida: {orden}")

if __name__ == "__main__":
    main()