import xmltodict
import json

def convert_xml_to_json(xml_file_path, json_file_path):
    with open(xml_file_path, 'r', encoding='utf-8') as file:
        xml_string = file.read()

    # Parse the XML string to a dictionary
    xml_dict = xmltodict.parse(xml_string)

    # Convert the dictionary to a JSON string
    json_string = json.dumps(xml_dict, indent=4)

    # Write the JSON string to a file
    with open(json_file_path, 'w') as file:
        file.write(json_string)

def convert_SUMO_to_FIWARE(originalSUMO, originalFIWARE, element):
    # Open the source JSON file and load the data
    with open(originalSUMO, 'r') as source_file:
        data = json.load(source_file)

    # ---------------------------------------------------------------------

    # TRANSPORTATION TYPE MAPPING
        
    # Define a mapping from transportation types to numbers
    transportation_type_mapping = {
        'tram': 0,
        'subway': 1,
        'rail': 2,
        'bus': 3,
        'ferry': 4,
        'cable_tram': 5,
        'aerial_lift': 6,
        'funicular': 7,
        'trolleybus': 11,
        'monorail': 12,
    }

    # Extract the transportation type from the source data
    transportation_type = data['ptLines']['plLine'][element]['@vClass']

    # Map the transportation type to a number
    transportation_type_number = transportation_type_mapping.get(transportation_type, None)

    # ---------------------------------------------------------------------

    # ROUTE COLOR MAPPING
        
    # Extract the routeColor from the source data
    route_color = data['ptLines']['ptLine'][element]['@color']

    # Split the string into separate numbers
    r, g, b = map(int, route_color.split(','))

    # Convert each number to hexadecimal and concatenate them together
    route_color_hex = '#{:02x}{:02x}{:02x}'.format(r, g, b)

    # ---------------------------------------------------------------------

    # Extract the id from the route field and create a new dictionary
    converted_data = {
        'id': data['ptLines']['ptLine'][element]['@id'],
        'type': 'PublicTransportRoute',
        'routeCode': '?',
        'name': data['ptLines']['ptLine'][element]['@name'],
        'transportationType': transportation_type_number,
        'routeColor': route_color_hex,
        'routeSegments': data['ptLines']['ptLine'][element]['busStop'][0]["@name"], # PENDIENTE
    }

    # Open the destination JSON file and dump the converted data
    with open(originalFIWARE, 'w') as destination_file:
        json.dump(converted_data, destination_file, indent=4)