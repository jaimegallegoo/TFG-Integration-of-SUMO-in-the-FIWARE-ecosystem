import sys
from lib import convert_xml_to_json, convert_SUMO_to_FIWARE

def main():

    # Establecer la posición de la orden en la línea de argumentos
    orden = sys.argv[1]

    if orden == "XMLtoJSON":
        xml_file_path = sys.argv[2]
        json_file_path = sys.argv[3]
        convert_xml_to_json(xml_file_path, json_file_path)
    #python app.py XMLtoJSON input_file.xml output_file.json

    elif orden == "SUMOtoFIWARE":
        originalSUMO = sys.argv[2]
        originalFIWARE = sys.argv[3]
        convert_SUMO_to_FIWARE(originalSUMO, originalFIWARE, 1)
    #python app.py SUMOtoFIWARE input_file.json output_file.json

    else:
        print(f"Orden no reconocida: {orden}")

if __name__ == "__main__":
    main()