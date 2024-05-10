import os
import requests
import xmltodict
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

# ---------------------------------------------------------------------
# ---------------------------------------------------------------------

# This function converts a route from a FIWARE modifiedFIWAREroute.json to a SUMO line in XML
def convert_FIWARE_route_to_SUMO_line(modifiedFIWAREroute, osm_ptlines):
    # Open the source JSON file and load the data
    with open(modifiedFIWAREroute, 'r') as source_file:
        data = json.load(source_file)

    # ---------------------------------------------------------------------

    # TRANSPORTATION TYPE MAPPING
        
    # Define a mapping from numbers to vClass
    vClass_mapping = {
        0: 'tram',
        1: 'rail_urban',
        2: 'rail',
        3: 'bus',
        4: 'ship',
        5: 'rail_urban',
        6: 'rail_urban',
        7: 'rail_urban',
        11: 'bus',
        12: 'rail_urban',
    }

    # Define a mapping from numbers to types
    type_mapping = {
        0: 'tram',
        1: 'subway',
        2: 'train',
        3: 'bus',
        4: 'ferry',
        5: 'tram',
        6: 'aerialway',
        7: 'tram',
        11: 'trolleybus',
        12: 'monorail',
    }

    # ---------------------------------------------------------------------

    # Create the root element
    root = ET.Element("ptLines", {"xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance", "xsi:noNamespaceSchemaLocation": "http://sumo.dlr.de/xsd/ptlines_file.xsd"})

    # Iterate over the data
    for item in data:

        # ---------------------------------------------------------------------

        # TRANSPORTATION TYPE MAPPING

        # Extract the transportation type from the source data
        transportation_type_number = item['transportationType']['value']

        # Map the vClass from the transportation type number
        vClass = vClass_mapping.get(transportation_type_number, "No data available")

        # Map the type from the transportation type number
        type = type_mapping.get(transportation_type_number, "No data available")
        # ---------------------------------------------------------------------

        # ROUTE COLOR MAPPING

        # Extract the routeColor from the source data
        route_color_hex = item['routeColor']['value']

        # Check if the routeColor is None
        if route_color_hex is None:
            route_color = "No data available"
        else:
            # Check if the routeColor is in the format '#rrggbb'
            if route_color_hex.startswith('#'):
                # Remove the '#' from the start of the string
                route_color_hex = route_color_hex[1:]

                # Split the string into separate pairs of hexadecimal digits
                r, g, b = route_color_hex[:2], route_color_hex[2:4], route_color_hex[4:]

                # Convert each pair of hexadecimal digits to an integer
                route_color = '{},{},{}'.format(int(r, 16), int(g, 16), int(b, 16))
            else:
                # If the routeColor is not in the format '#rrggbb', use it as is
                route_color = route_color_hex

        # ---------------------------------------------------------------------

        # Create a new ptLine XML element and set its attributes
        ptLine = ET.SubElement(root, "ptLine", {
            "id": item['routeCode']['value'],
            "name": item['name']['value'],
            "line": item['shortRouteCode']['value'],
            "type": type,
            "vClass": vClass,
            "period": "PENDIENTE",
            "color": route_color,
            "completeness": "PENDIENTE" 
        })

        # Create a busStop child element for each stop in the route segments
        for segment in item['routeSegments']['value']:
            # Check if segment is a dictionary
            if isinstance(segment, dict):
                # Take only the first stop
                stop = segment['refPublicTransportStops'][0]
                # Split the segment name by '-' and take the first part
                first_name = segment['segmentName'].split('-')[0].strip()
                busStop = ET.SubElement(ptLine, "busStop", {
                    "id": stop.split(':')[-1],
                    "name": first_name
                })
            else:
                # If segment is not a dictionary, print it out
                print(f"Unexpected segment: {segment}")

    # Create an ElementTree object and write it to a file
    tree = ET.ElementTree(root)
    # tree.write(originalSUMOline, xml_declaration=True, encoding='UTF-8')

    # Convert the ElementTree to a string
    xml_string = ET.tostring(root, encoding='utf-8')

    # Parse the string with minidom
    dom = minidom.parseString(xml_string)

    # Use toprettyxml to format the XML
    pretty_xml = dom.toprettyxml(indent="  ")

    # Add the encoding to the XML declaration
    pretty_xml = pretty_xml.replace('<?xml version="1.0" ?>', '<?xml version="1.0" encoding="UTF-8"?>')

    # Write the formatted XML to a file
    with open(osm_ptlines, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------

# FUNCTIONS FOR THE WEB INTERFACE

# This function converts the lines and stops from the selected city in the application to SUMO
def convert_FIWARE_city(city):
    # Create the folder for the SUMO output files
    modifiedSUMOfolder = f'../../../data/output/sumo/{city}'
    os.makedirs(modifiedSUMOfolder, exist_ok=True)

    # Define the path for the SUMO input original files
    originalSUMOfolder = f'../../../data/input/sumo/{city}'

    # Copy the original files to the modified folder
    os.system(f'cp {originalSUMOfolder}/* {modifiedSUMOfolder}')

    # Delete the files osm_ptlines.xml and osm_stops.add.xml from the modified folder
    os.system(f'rm {modifiedSUMOfolder}/osm_ptlines.xml')
    os.system(f'rm {modifiedSUMOfolder}/osm_stops.add.xml')

    # Create temporal JSON files for the FIWARE input data
    modifiedFIWAREroute = '../../../data/temporal/modifiedFIWAREroute.json'
    modifiedFIWAREstop = '../../../data/temporal/modifiedFIWAREstop.json'

    # Get the modified files in FIWARE format from the Orion Context Broker
    routes = get_entity(city, 'PublicTransportRoute')
    stops = get_entity(city, 'PublicTransportStop')

    # Write the files to the temporal folder as JSON
    with open(modifiedFIWAREroute, 'w') as file:
        json.dump(routes, file, indent=4)
    with open(modifiedFIWAREstop, 'w') as file:
        json.dump(stops, file, indent=4)

    # Create the files for the SUMO output
    osm_ptlines = f'../../../data/output/sumo/{city}/osm_ptlines.xml'
    osm_stops = f'../../../data/output/sumo/{city}/osm_stops.add.xml'

    # Convert the routes and stops to SUMO format
    convert_FIWARE_route_to_SUMO_line(modifiedFIWAREroute, osm_ptlines)
    #convert_FIWARE_stop_to_SUMO_stop(modifiedFIWAREstop, osm_stops)

    # Delete the temporal JSON files
    os.remove(modifiedFIWAREroute) 
    os.remove(modifiedFIWAREstop)

# ---------------------------------------------------------------------

# This function gets the entities from the Orion Context Broker
def get_entity(city, type):
    response = requests.get(f'http://localhost:1026/v2/entities/?type={type}&q=address.addressLocality=={city.capitalize()}&limit=1000')
    if response.status_code == 200:
        print("Entities retrieved successfully")
        return response.json()
    else:
        print("Failed to retrieve entities")
        print(response.text)