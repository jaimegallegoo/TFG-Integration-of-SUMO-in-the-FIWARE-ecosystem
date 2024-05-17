import os
import requests
import xmltodict
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

# ---------------------------------------------------------------------
# ---------------------------------------------------------------------

# This function converts a route from a FIWARE modifiedFIWAREroute.json to a SUMO line in XML
def convert_FIWARE_route_to_SUMO_line(modifiedFIWAREroute, osm_ptlines, city):
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

        # MAPPING FOR THE ELEMENTS NOT STORED IN THE FIWARE DATA

        # Open the original SUMO line file and load the data
        with open(f'../../../data/input/sumo/{city}/osm_ptlines.xml', 'r', encoding='utf-8') as source_file:
            original_data = xmltodict.parse(source_file.read())

        # Extract the ptLine elements from the original data
        original_ptLines = original_data['ptLines']['ptLine']

        # Iterate over the original ptLine elements
        for original_ptLine in original_ptLines:
            # Check if the id of the original ptLine element matches the id of the current item
            if original_ptLine['@id'] == item['routeCode']['value']:

                # Extract the data from the original ptLine element

                # PERIOD MAPPING
                period = original_ptLine.get('@period', 'No data available')

                # COMPLETENESS MAPPING
                completeness = original_ptLine.get('@completeness', 'No data available')

                # ROUTE EDGES MAPPING
                route_edges = original_ptLine['route']['@edges'] if 'route' in original_ptLine else 'No data available'

                break

        # ---------------------------------------------------------------------

        # Create a new ptLine XML element and set its attributes
        ptLine = ET.SubElement(root, "ptLine", {
            "id": item['routeCode']['value'],
            "name": item['name']['value'],
            "line": item['shortRouteCode']['value'],
            "type": type,
            "vClass": vClass,
            "period": period,
            "color": route_color,
            "completeness": completeness 
        })

        # Create a route child element for the route edges
        route = ET.SubElement(ptLine, "route", {
            "edges": route_edges
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

# This function converts a stop from a FIWARE modifiedFIWAREstop.json to a SUMO stop in XML
def convert_FIWARE_stop_to_SUMO_stop(modifiedFIWAREstop, osm_stops, city):
    # Open the source JSON file and load the data
    with open(modifiedFIWAREstop, 'r') as source_file:
        data = json.load(source_file)

    # ---------------------------------------------------------------------

    # Create the root element
    root = ET.Element("additional", {"xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance", "xsi:noNamespaceSchemaLocation": "http://sumo.dlr.de/xsd/additional_file.xsd"})

    # Iterate over the data
    for item in data:

        # ---------------------------------------------------------------------

        # LINES MAPPING

        # Extract the lines from the source data
        lines = item['refPublicTransportRoute']['value']

        # Extract the line codes from the URNs
        line_codes = [line.split(':')[-1] for line in lines]

        # Join the line codes into a string
        line_string = ' '.join(line_codes)

        # ---------------------------------------------------------------------

        # MAPPING FOR THE ELEMENTS NOT STORED IN THE FIWARE DATA

        # Open the original SUMO stop file and load the data
        with open(f'../../../data/input/sumo/{city}/osm_stops.add.xml', 'r', encoding='utf-8') as source_file:
            original_data = xmltodict.parse(source_file.read())

        # Extract the busStop elements from the original data
        original_busStops = original_data['additional']['busStop']

        # Iterate over the original busStop elements
        for original_busStop in original_busStops:
            # Check if the id of the original busStop element matches the id of the current item
            if original_busStop['@id'] == item['stopCode']['value']:

                # Extract the data from the original ptLine element

                # LANE MAPPING
                lane = original_busStop.get('@lane', 'No data available')

                # START POSITION MAPPING
                startPos = original_busStop.get('@startPos', 'No data available')

                # END POSITION MAPPING
                endPos = original_busStop.get('@endPos', 'No data available')

                # FRIENDLY POSITION MAPPING
                friendlyPos = original_busStop.get('@friendlyPos', 'No data available')

                # ACCESS MAPPING
                access_elements = original_busStop.get('access', [])
                if isinstance(access_elements, dict):
                    access_elements = [access_elements]
                access_lanes = [
                    {
                        'lane': access['@lane'],
                        'pos': access['@pos'],
                        'length': access['@length'],
                        'friendlyPos': access['@friendlyPos']
                    } for access in access_elements] if 'access' in original_busStop else 'No data available'

                break

        # ---------------------------------------------------------------------

        # Create a new busStop XML element and set its attributes
        busStop = ET.SubElement(root, "busStop", {
            "id": item['stopCode']['value'],
            "name": item['name']['value'],
            "lane": lane,
            "startPos": startPos,
            "endPos": endPos,
            "friendlyPos": friendlyPos,
            "lines": line_string
        })

        # Create an access child element for each access lane
        if isinstance(access_lanes, list):
            for access_lane in access_lanes:
                access = ET.SubElement(busStop, "access", {
                    "lane": access_lane['lane'],
                    "pos": access_lane['pos'],
                    "length": access_lane['length'],
                    "friendlyPos": access_lane['friendlyPos']
                })


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
    with open(osm_stops, 'w', encoding='utf-8') as f:
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

    # Delete the files osm_ptlines.xml, osm_stops.add.xml and osm_pt.rou.xml from the modified folder
    os.system(f'rm {modifiedSUMOfolder}/osm_ptlines.xml')
    os.system(f'rm {modifiedSUMOfolder}/osm_stops.add.xml')
    os.system(f'rm {modifiedSUMOfolder}/osm_pt.rou.xml')

    # Create temporal JSON files for the FIWARE input data
    modifiedFIWAREroute = '../../../data/temporal/modifiedFIWAREroute.json'
    modifiedFIWAREstop = '../../../data/temporal/modifiedFIWAREstop.json'

    # Get the modified files in FIWARE format from the Orion Context Broker
    routes = get_entities_web(city, 'PublicTransportRoute')
    stops = get_entities_web(city, 'PublicTransportStop')

    # Write the files to the temporal folder as JSON
    with open(modifiedFIWAREroute, 'w') as file:
        json.dump(routes, file, indent=4)
    with open(modifiedFIWAREstop, 'w') as file:
        json.dump(stops, file, indent=4)

    # Create the files for the SUMO output
    osm_ptlines = f'../../../data/output/sumo/{city}/osm_ptlines.xml'
    osm_stops = f'../../../data/output/sumo/{city}/osm_stops.add.xml'

    # Convert the routes and stops to SUMO format
    convert_FIWARE_route_to_SUMO_line(modifiedFIWAREroute, osm_ptlines, city)
    convert_FIWARE_stop_to_SUMO_stop(modifiedFIWAREstop, osm_stops, city)

    # Generate the routes file based on the lines and stops
    sumo_home = os.getenv('SUMO_HOME') # C:\Program Files (x86)\Eclipse\Sumo
    osm_net = f'../../../data/output/sumo/{city}/osm.net.xml.gz'
    stop_infos = f'../../../data/output/sumo/{city}/stopinfos.xml'
    trips = f'../../../data/output/sumo/{city}/trips.trips.xml'
    veh_routes = f'../../../data/output/sumo/{city}/vehroutes.xml'
    osm_routes = f'../../../data/output/sumo/{city}/osm_pt.rou.xml'
    os.system(f'python "{sumo_home}/tools/ptlines2flows.py" -n {osm_net} -s {osm_stops} -l {osm_ptlines} -i {stop_infos} -t {trips} -r {veh_routes} -o {osm_routes} --ignore-errors --min-stops 0')
    
    # Delete the temporal JSON files
    os.remove(modifiedFIWAREroute) 
    os.remove(modifiedFIWAREstop)

# ---------------------------------------------------------------------

# This function gets the entities from the Orion Context Broker
def get_entities(city, type):
    response = requests.get(f'http://localhost:1026/v2/entities/?type={type}&q=address.addressLocality=={city.capitalize()}&limit=1000')
    if response.status_code == 200:
        print("Entities retrieved successfully")
        return response.json()
    else:
        print("Failed to retrieve entities")
        print(response.text)

# This function gets the entities from the Orion Context Broker
def get_entities_web(city, type):
    # Use the ORION_URL environment variable
    orion_url = os.getenv('ORION_URL', 'http://localhost:1026')
    response = requests.get(f'{orion_url}/v2/entities/?type={type}&q=address.addressLocality=={city.capitalize()}&limit=1000')
    if response.status_code == 200:
        print("Entities retrieved successfully")
        return response.json()
    else:
        print("Failed to retrieve entities")
        print(response.text)