import sys
from functions_fiware_to_sumo import *

def main():

    # Establecer la posición de la orden en la línea de argumentos
    orden = sys.argv[1]

    if orden == "FIWARE_to_SUMO_route":
        modifiedFIWAREroute = sys.argv[2]
        osm_ptlines = sys.argv[3]
        convert_FIWARE_route_to_SUMO_line(modifiedFIWAREroute, osm_ptlines)
    #python main_fiware_to_sumo.py FIWARE_to_SUMO_route originalFIWAREroute.json prueba.xml

    elif orden == "FIWARE_to_SUMO_stop":
        modifiedFIWAREstop = sys.argv[2]
        osm_stops = sys.argv[3]
        convert_FIWARE_stop_to_SUMO_stop(modifiedFIWAREstop, osm_stops)
    #python main_fiware_to_sumo.py FIWARE_to_SUMO_stop originalFIWAREstop.json prueba.xml

    elif orden == "city":
        city = sys.argv[2]
        convert_FIWARE_city(city)
    #python main_fiware_to_sumo.py city madrid

    elif orden == "get_entities":
        city = sys.argv[2]
        type = sys.argv[3]
        get_entities(city, type)
    #python main_fiware_to_sumo.py get_entities madrid PublicTransportRoute

    else:
        print(f"Orden no reconocida: {orden}")

if __name__ == "__main__":
    main()