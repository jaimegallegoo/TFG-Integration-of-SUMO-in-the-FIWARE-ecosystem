import sys
from functions import *

def main():

    # Establecer la posición de la orden en la línea de argumentos
    orden = sys.argv[1]

    if orden == "XMLtoJSON":
        xml_file_path = sys.argv[2]
        json_file_path = sys.argv[3]
        convert_xml_to_json(xml_file_path, json_file_path)
    #python main.py XMLtoJSON input_file.xml output_file.json

    elif orden == "SUMO_line_to_FIWARE_route":
        originalSUMOline = sys.argv[2]
        originalFIWAREroute = sys.argv[3]
        convert_SUMO_line_to_FIWARE_route(originalSUMOline, originalFIWAREroute, 1)
    #python main.py SUMO_line_to_FIWARE_route input_file.json output_file.json
        
    # Con esta orden se hacen las dos anteriores en una sola
    elif orden == "SUMO_line":
        originalSUMOlineXML = sys.argv[2]
        convert_SUMO_line(originalSUMOlineXML)
    #python main.py SUMO_line osm_ptlines.xml
        
    elif orden == "SUMO_stop_to_FIWARE_stop":
        originalSUMOstop = sys.argv[2]
        originalFIWAREstop = sys.argv[3]
        convert_SUMO_stop_to_FIWARE_stop(originalSUMOstop, originalFIWAREstop, 2)
    #python main.py SUMO_stop_to_FIWARE_stop input_file.json output_file.json

    # Con esta orden se hacen las dos anteriores en una sola
    elif orden == "SUMO_stop":
        originalSUMOstopXML = sys.argv[2]
        convert_SUMO_stop(originalSUMOstopXML)
    #python main.py SUMO_stop osm_stops.add.xml

    else:
        print(f"Orden no reconocida: {orden}")

if __name__ == "__main__":
    main()