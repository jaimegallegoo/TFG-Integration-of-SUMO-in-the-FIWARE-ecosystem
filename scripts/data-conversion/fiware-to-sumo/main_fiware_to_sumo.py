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

    elif orden == "city":
        city = sys.argv[2]
        convert_FIWARE_city(city)
    #python main_fiware_to_sumo.py city madrid

    elif orden == "get_entities":
        city = sys.argv[2]
        type = sys.argv[3]
        get_entity(city, type)
    #python main_fiware_to_sumo.py get_entities madrid PublicTransportRoute

    else:
        print(f"Orden no reconocida: {orden}")

if __name__ == "__main__":
    main()