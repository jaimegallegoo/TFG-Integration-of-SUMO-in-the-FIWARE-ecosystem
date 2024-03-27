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

def convert_SUMO_to_FIWARE(originalSUMO, originalFIWARE):
    # Open the source JSON file and load the data
    with open(originalSUMO, 'r') as source_file:
        data = json.load(source_file)

    # ---------------------------------------------------------------------

    # TRANSPORTATION TYPE MAPPING
        
    # Define a mapping from transportation types to numbers
    transportation_type_mapping = {
        'pt_tram': 0,
        'pt_subway': 1,
        'pt_rail': 2,
        'pt_bus': 3,
        'pt_ferry': 4,
        'pt_cable_tram': 5,
        'pt_aerial_lift': 6,
        'pt_funicular': 7,
        'pt_trolleybus': 11,
        'pt_monorail': 12,
    }

    # Extract the transportation type from the source data
    transportation_type = data['routes']['flow'][0]['@type']

    # Map the transportation type to a number
    transportation_type_number = transportation_type_mapping.get(transportation_type, None)

    # ---------------------------------------------------------------------

    # ROUTE COLOR MAPPING
        
    # Extract the routeColor from the source data
    route_color = data['routes']['route'][0]['@color']

    # Split the string into separate numbers
    r, g, b = map(int, route_color.split(','))

    # Convert each number to hexadecimal and concatenate them together
    route_color_hex = '#{:02x}{:02x}{:02x}'.format(r, g, b)

    # ---------------------------------------------------------------------

    # Extract the id from the route field and create a new dictionary
    converted_data = {
        'id': data['routes']['route'][0]['@id'],
        'type': 'PublicTransportRoute',
        'routeCode': data['routes']['route'][0]['@id'],
        'name': data['routes']['flow'][0]['param'][0]['@value'],
        'transportationType': transportation_type_number,
        'routeColor': route_color_hex,
        'routeSegments': '?',
    }

    # Open the destination JSON file and dump the converted data
    with open(originalFIWARE, 'w') as destination_file:
        json.dump(converted_data, destination_file, indent=4)