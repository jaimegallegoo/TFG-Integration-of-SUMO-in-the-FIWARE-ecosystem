import xmltodict
import json

# Global variables

city = 'santander'

# ---------------------------------------------------------------------
# ---------------------------------------------------------------------

# This function converts an XML file to a JSON file
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

# ---------------------------------------------------------------------
# ---------------------------------------------------------------------

# This function converts a line from a SUMO osm_ptline to a FIWARE PublicTransportRoute
def convert_SUMO_line_to_FIWARE_route(originalSUMOline, originalFIWAREroute, element):
    # Open the source JSON file and load the data
    with open(originalSUMOline, 'r') as source_file:
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
    transportation_type = data['ptLines']['ptLine'][element]['@vClass']

    # Map the transportation type to a number
    transportation_type_number = transportation_type_mapping.get(transportation_type, None)

    # ---------------------------------------------------------------------

    # ROUTE COLOR MAPPING

    # Extract the routeColor from the source data
    route_color = data['ptLines']['ptLine'][element]['@color']

    # Check if the routeColor is in the format 'r,g,b'
    if ',' in route_color:
        # Split the string into separate numbers
        r, g, b = map(int, route_color.split(','))

        # Convert each number to hexadecimal
        route_color_hex = '#{:02x}{:02x}{:02x}'.format(r, g, b)
    else:
        # Map the color name to its corresponding hexadecimal value
        color_mapping = {
            'red': '#ff0000',
            'green': '#00ff00',
            'blue': '#0000ff',
            # ...
        }

        # Get the hexadecimal value for the color name
        route_color_hex = color_mapping.get(route_color.lower(), None)

    # ---------------------------------------------------------------------
        
    # LINE MAPPING

    # Extract the transportation line from the source data
    line = data['ptLines']['ptLine'][element]['@line']

    # ---------------------------------------------------------------------

    # ROUTE SEGMENTS MAPPING

    bus_stops = data['ptLines']['ptLine'][element]['busStop']
    route_segments = []

    for i in range(len(bus_stops) - 1):
        segment = {
            'segmentName': bus_stops[i]['@name'] + ' - ' + bus_stops[i+1]['@name'],
            'refPublicTransportStops': [
                f'urn:ngsi-ld:PublicTransportStop:{city}:transport:busStop:' + bus_stops[i]['@id'],
                f'urn:ngsi-ld:PublicTransportStop:{city}:transport:busStop:' + bus_stops[i+1]['@id']
            ]
        }
        route_segments.append(segment)

    # ---------------------------------------------------------------------

    # Create a new dictionary in NGSI-v2 (keyvalues) with the converted data
    converted_data = {
        'id': f'urn:ngsi-ld:PublicTransportRoute:{city}:transport:busLine:{line}', # PENDIENTE. Hay que hacer que en vez de Santander y busLine se pongan los valores correctos.
        'type': 'PublicTransportRoute',
        'routeCode': data['ptLines']['ptLine'][element]['@id'],
        'shortRouteCode': line,
        'name': data['ptLines']['ptLine'][element]['@name'],
        'transportationType': transportation_type_number,
        'routeColor': route_color_hex,
        'routeSegments': route_segments
    }

    # Create a new dictionary in NGSI-v2 (normalized) with the converted data
    converted_data_normalized = {
        'id': f'urn:ngsi-ld:PublicTransportRoute:santander:transport:busLine:{line}', # PENDIENTE. Hay que hacer que en vez de Santander y busLine se pongan los valores correctos.
        'type': 'PublicTransportRoute',
        'routeCode': {
            'type': 'Text',
            'value': data['ptLines']['ptLine'][element]['@id']
        },
        'shortRouteCode': {
            'type': 'Text',
            'value': line
        },
        'name': {
            'type': 'Text',
            'value': data['ptLines']['ptLine'][element]['@name']
        },
        'transportationType': {
            'type': 'Number',
            'value': transportation_type_number
        },
        'routeColor': {
            'type': 'Text',
            'value': route_color_hex
        },
        'routeSegments': {
            'type': 'StructuredValue',
            'value': route_segments
        }
    }

    # Open the destination JSON file and dump the converted data
    with open(originalFIWAREroute, 'w') as destination_file:
        json.dump(converted_data_normalized, destination_file, indent=4)

# ---------------------------------------------------------------------
# ---------------------------------------------------------------------

# This function converts a line from a SUMO "osm_ptlines.xml" to a FIWARE PublicTransportRoute
def convert_SUMO_line(originalSUMOlineXML):
    originalSUMOlineJSON = 'originalSUMOlineJSON.json'
    originalFIWAREroute = 'originalFIWAREroute.json'
    convert_xml_to_json(originalSUMOlineXML, originalSUMOlineJSON)
    convert_SUMO_line_to_FIWARE_route(originalSUMOlineJSON, originalFIWAREroute, 0)

# ---------------------------------------------------------------------
# ---------------------------------------------------------------------

# This function converts a stop from a SUMO "osm_stop.xml" to a FIWARE PublicTransportStop
def convert_SUMO_stop_to_FIWARE_stop(originalSUMOstop, originalFIWAREstop, element):
    # Open the source JSON file and load the data
    with open(originalSUMOstop, 'r') as source_file:
        data = json.load(source_file)

    # ---------------------------------------------------------------------
        
    # STOP MAPPING

    # Extract the transportation stop from the source data
    id = data['additional']['busStop'][element]['@id']

    # ---------------------------------------------------------------------

    # LINES MAPPING

    # Extract the transportation lines from the source data
    lines = data['additional']['busStop'][element]['@lines']

    # Split the string into separate values
    lines_array = lines.split()

    # ---------------------------------------------------------------------

    # Create a new dictionary with the converted data
    converted_data = {
        'id': f'urn:ngsi-ld:PublicTransportStop:{city}:busStop:{id}', # PENDIENTE. Hay que hacer que en vez de Santander y busLine se pongan los valores correctos.
        'type': 'PublicTransportStop',
        'stopCode': id,
        'name': data['additional']['busStop'][element]['@name'],
        'transportationType': '?',
        'refPublicTransportRoute': [
            f'urn:ngsi-ld:PublicTransportRoute:{city}:transport:busLine:{line}' for line in lines_array
        ],
    }

    # Open the destination JSON file and dump the converted data
    with open(originalFIWAREstop, 'w') as destination_file:
        json.dump(converted_data, destination_file, indent=4)

    