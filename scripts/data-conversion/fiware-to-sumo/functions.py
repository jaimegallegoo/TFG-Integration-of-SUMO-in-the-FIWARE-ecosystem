import xmltodict
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Global variables

city = 'santander'

# ---------------------------------------------------------------------
# ---------------------------------------------------------------------

# This function converts a route from a FIWARE originalFIWAREroute.json to a SUMO line in XML
def convert_FIWARE_route_to_SUMO_line(originalFIWAREroute, originalSUMOline):
    # Open the source JSON file and load the data
    with open(originalFIWAREroute, 'r') as source_file:
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
        # Extract the transportation type from the source data
        transportation_type_number = item['transportationType']['value']

        # Map the vClass from the transportation type number
        vClass = vClass_mapping.get(transportation_type_number, "No data available")

        # Map the type from the transportation type number
        type = type_mapping.get(transportation_type_number, "No data available")
        # ---------------------------------------------------------------------

        # Create a new ptLine XML element and set its attributes
        ptLine = ET.SubElement(root, "ptLine", {
            "id": item['routeCode']['value'],
            "name": item['name']['value'],
            "line": item['shortRouteCode']['value'],
            "type": type,
            "vClass": vClass,
            "period": "PENDIENTE",
            "color": "PENDIENTE",
            "completeness": "PENDIENTE" 
        })

        # Create a route child element and set its attributes
        '''
        route = ET.SubElement(ptLine, "route", {
            "edges": " ".join(segment['refPublicTransportStops'] for segment in item['routeSegments']['value'])
        })
        '''

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
    with open(originalSUMOline, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    