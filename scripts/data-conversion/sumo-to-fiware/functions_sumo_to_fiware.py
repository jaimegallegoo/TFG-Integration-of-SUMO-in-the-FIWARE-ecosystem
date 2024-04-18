import os
import xmltodict
import json

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
def convert_SUMO_line_to_FIWARE_route(originalSUMOline, originalFIWAREroute, city, element):
    # Open the source JSON file and load the data
    with open(originalSUMOline, 'r') as source_file:
        data = json.load(source_file)

    # ---------------------------------------------------------------------

    # TRANSPORTATION TYPE MAPPING
        
    # Define a mapping from transportation types to numbers
    transportation_type_mapping = {
        'tram': 0,
        'subway': 1,
        'train': 2,
        'bus': 3,
        'ferry': 4,
        'aerialway': 6,
        'trolleybus': 11,
        'monorail': 12,
    }

    # Extract the transportation type from the source data

    # REVISAR, A VECES VIENE COMO vClass Y OTRAS COMO type
    #transportation_type = data['ptLines']['ptLine'][element]['@vClass']
    transportation_type = data['ptLines']['ptLine'][element]['@type']

    # Map the transportation type to a number
    transportation_type_number = transportation_type_mapping.get(transportation_type, None)

    # ---------------------------------------------------------------------

    # ROUTE COLOR MAPPING

    # Extract the routeColor from the source data
    route_color = data['ptLines']['ptLine'][element].get('@color')

    # Check if the routeColor is None
    if route_color is None:
        route_color_hex = "No data available"
    else:
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
                'white': '#ffffff',
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

    #bus_stops = data['ptLines']['ptLine'][element]['busStop']
    bus_stops = data['ptLines']['ptLine'][element].get('busStop')

    # Check if bus_stops is not None
    if bus_stops:
        # If bus_stops is a dictionary, convert it to a list
        if isinstance(bus_stops, dict):
            bus_stops = [bus_stops]

        route_segments = []

        # Check if there is only one element in bus_stops
        if len(bus_stops) == 1:
            segment = {
                'segmentName': bus_stops[0]['@name'],
                'refPublicTransportStops': [
                    f'urn:ngsi-ld:PublicTransportStop:{city}:transport:busStop:' + bus_stops[0]['@id']
                ]
            }
            route_segments.append(segment)

        else:
            for i in range(len(bus_stops) - 1):
                segment = {
                    'segmentName': bus_stops[i]['@name'] + ' - ' + bus_stops[i+1]['@name'],
                    'refPublicTransportStops': [
                        f'urn:ngsi-ld:PublicTransportStop:{city}:transport:busStop:' + bus_stops[i]['@id'],
                        f'urn:ngsi-ld:PublicTransportStop:{city}:transport:busStop:' + bus_stops[i+1]['@id']
                    ]
                }
                route_segments.append(segment)
    else:
        route_segments = "No data available"    

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
        'id': f'urn:ngsi-ld:PublicTransportRoute:{city}:transport:busLine:{line}', # PENDIENTE. Hay que hacer que en vez de Santander y busLine se pongan los valores correctos.
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

    # Check if the file exists
    if not os.path.isfile(originalFIWAREroute):
        # If not, create it by opening it in write mode
        with open(originalFIWAREroute, 'w') as destination_file:
            json.dump([], destination_file)

    # Open the destination JSON file and load the existing data
    with open(originalFIWAREroute, 'r') as destination_file:
        try:
            existing_data = json.load(destination_file)
        except json.JSONDecodeError:
            existing_data = []

    # Append the converted data to the existing data
    existing_data.append(converted_data_normalized)

    # Open the destination JSON file again and dump the updated data
    with open(originalFIWAREroute, 'w') as destination_file:
        json.dump(existing_data, destination_file, indent=4)

# ---------------------------------------------------------------------
# ---------------------------------------------------------------------

# This function converts a line from a SUMO "osm_ptlines.xml" to a FIWARE PublicTransportRoute
def convert_SUMO_line(originalSUMOlineXML, originalFIWAREroute, city):

    # Create a temporal JSON file for the SUMO input data
    originalSUMOlineJSON = '../../../data/temporal/originalSUMOlineJSON.json'

    # Convert the XML file to a JSON file
    convert_xml_to_json(originalSUMOlineXML, originalSUMOlineJSON)

    # Load the JSON file into a Python object
    with open(originalSUMOlineJSON) as f:
        data = json.load(f)

    # Get the "ptLine" list
    ptLine_list = data['ptLines']['ptLine']

    # Iterate over each element in the "ptLine" list
    for i, ptLine in enumerate(ptLine_list):
        # Call convert_SUMO_line_to_FIWARE_route for each "ptLine"
        convert_SUMO_line_to_FIWARE_route(originalSUMOlineJSON, originalFIWAREroute, city, i)

# ---------------------------------------------------------------------
# ---------------------------------------------------------------------

# This function converts a stop from a SUMO "osm_stop.xml" to a FIWARE PublicTransportStop
def convert_SUMO_stop_to_FIWARE_stop(originalSUMOstop, originalFIWAREstop, city, element):
    # Open the source JSON file and load the data
    with open(originalSUMOstop, 'r') as source_file:
        data = json.load(source_file)

    # ---------------------------------------------------------------------
        
    # STOP MAPPING

    # Extract the transportation stop from the source data
    id = data['additional']['busStop'][element]['@id']

    # ---------------------------------------------------------------------
        
    # NAME MAPPING

    # Extract the transportation stop name from the source data
    name = data['additional']['busStop'][element].get('@name')

    if name is None:
        name = "No data available"

    # ---------------------------------------------------------------------

    # LINES MAPPING

    # Extract the transportation lines from the source data if present
    lines = data['additional']['busStop'][element].get('@lines')

    # Proceed only if lines is not None
    if lines is not None:
        # Split the string into separate values
        lines_array = lines.split()

    # Check if lines_array exists and is not empty
    if 'lines_array' in locals() and lines_array:
        refPublicTransportRoute = [
            f'urn:ngsi-ld:PublicTransportRoute:{city}:transport:busLine:{line}' for line in lines_array
        ]
    else:
        refPublicTransportRoute = "No data available"

    # ---------------------------------------------------------------------

    # Create a new dictionary in NGSI-v2 (keyvalues) with the converted data
    converted_data = {
        'id': f'urn:ngsi-ld:PublicTransportStop:{city}:busStop:{id}', # PENDIENTE. Hay que hacer que en vez de Santander y busLine se pongan los valores correctos.
        'type': 'PublicTransportStop',
        'stopCode': id,
        'name': name,
        'transportationType': '?',
        'refPublicTransportRoute': refPublicTransportRoute,
    }

    # Create a new dictionary in NGSI-v2 (normalized) with the converted data
    converted_data_normalized = {
        'id': f'urn:ngsi-ld:PublicTransportStop:{city}:busStop:{id}', # PENDIENTE. Hay que hacer que en vez de Santander y busLine se pongan los valores correctos.
        'type': 'PublicTransportStop',
        'stopCode': {
            'type': 'Text',
            'value': id
        },
        'name': {
            'type': 'Text',
            'value': name
        },
        'transportationType': {
            'type': 'StructuredValue',
            'value': [
            'PENDIENTE'
            ]
        },
        'refPublicTransportRoute': {
            'type': 'StructuredValue',
            'value': refPublicTransportRoute
        }
    }

    # Check if the file exists
    if not os.path.isfile(originalFIWAREstop):
        # If not, create it by opening it in write mode
        with open(originalFIWAREstop, 'w') as destination_file:
            json.dump([], destination_file)

    # Open the destination JSON file and load the existing data
    with open(originalFIWAREstop, 'r') as destination_file:
        try:
            existing_data = json.load(destination_file)
        except json.JSONDecodeError:
            existing_data = []

    # Append the converted data to the existing data
    existing_data.append(converted_data_normalized)

    # Open the destination JSON file again and dump the updated data
    with open(originalFIWAREstop, 'w') as destination_file:
        json.dump(existing_data, destination_file, indent=4)

# ---------------------------------------------------------------------
# ---------------------------------------------------------------------

# This function converts a stop from a SUMO "osm_stops.add.xml" to a FIWARE PublicTransportStop
def convert_SUMO_stop(originalSUMOstopXML, originalFIWAREstop, city):

    # Create a temporal JSON file for the SUMO input data
    originalSUMOstopJSON = '../../../data/temporal/originalSUMOstopJSON.json'

    # Convert the XML file to a JSON file
    convert_xml_to_json(originalSUMOstopXML, originalSUMOstopJSON)
    
    # Load the JSON file into a Python object
    with open(originalSUMOstopJSON) as f:
        data = json.load(f)

    # Get the "busStop" list
    busStop_list = data['additional']['busStop']

    # Iterate over each element in the "busStop" list
    for i, ptLine in enumerate(busStop_list):
        # Call convert_SUMO_line_to_FIWARE_route for each "busStop"
        convert_SUMO_stop_to_FIWARE_stop(originalSUMOstopJSON, originalFIWAREstop, city, i)    

# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------

# FUNCTIONS FOR THE WEB INTERFACE

# This function converts the lines and stops from the selected city in the application
def convert_SUMO_city(city):
    # Define the paths for the SUMO input files
    originalSUMOlineXML = f'../../../data/input/sumo/{city}/osm_ptlines.xml'
    originalSUMOstopXML = f'../../../data/input/sumo/{city}/osm_stops.add.xml'

    # Create the folder for the FIWARE output files
    originalFIWAREfolder = f'../../../data/output/fiware/{city}'
    os.makedirs(originalFIWAREfolder, exist_ok=True)

    # Define the paths for the FIWARE output files
    originalFIWAREroute = f'{originalFIWAREfolder}/originalFIWAREroute.json'
    originalFIWAREstop = f'{originalFIWAREfolder}/originalFIWAREstop.json'

    # Convert the lines and stops from the selected city
    convert_SUMO_line(originalSUMOlineXML, originalFIWAREroute, city)
    convert_SUMO_stop(originalSUMOstopXML, originalFIWAREstop, city)