import sys
from lib import convert_xml_to_json, convert_SUMO_line_to_FIWARE_route, convert_SUMO_stop_to_FIWARE_stop

def main():

    # Establecer la posición de la orden en la línea de argumentos
    orden = sys.argv[1]

    if orden == "XMLtoJSON":
        xml_file_path = sys.argv[2]
        json_file_path = sys.argv[3]
        convert_xml_to_json(xml_file_path, json_file_path)
    #python app.py XMLtoJSON input_file.xml output_file.json

    elif orden == "SUMO_line_to_FIWARE_route":
        originalSUMOline = sys.argv[2]
        originalFIWAREroute = sys.argv[3]
        convert_SUMO_line_to_FIWARE_route(originalSUMOline, originalFIWAREroute, 1)
    #python app.py SUMO_line_to_FIWARE_route input_file.json output_file.json
        
    elif orden == "SUMO_stop_to_FIWARE_stop":
        originalSUMOstop = sys.argv[2]
        originalFIWAREstop = sys.argv[3]
        convert_SUMO_stop_to_FIWARE_stop(originalSUMOstop, originalFIWAREstop, 2)
    #python app.py SUMO_stop_to_FIWARE_stop input_file.json output_file.json

    else:
        print(f"Orden no reconocida: {orden}")

if __name__ == "__main__":
    main()