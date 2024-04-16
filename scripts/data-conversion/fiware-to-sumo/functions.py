import xmltodict
import json
import xml.etree.ElementTree as ET

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

    # ---------------------------------------------------------------------

    # Create the root element
    root = ET.Element("ptLines", {"xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance", "xsi:noNamespaceSchemaLocation": "http://sumo.dlr.de/xsd/ptlines_file.xsd"})

    # Iterate over the data
    for item in data:
        # Create a new ptLine XML element and set its attributes
        ptLine = ET.SubElement(root, "ptLine", {
            "id": item['routeCode']['value'],
            "name": item['name']['value'],
            "line": item['shortRouteCode']['value'],
            "type": "PENDIENTE",
            "vClass": "PENDIENTE",
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
                for stop in segment['refPublicTransportStops']:
                    busStop = ET.SubElement(ptLine, "busStop", {
                        "id": stop.split(':')[-1],
                        "name": segment['segmentName']
                    })
            else:
                # If segment is not a dictionary, print it out
                print(f"Unexpected segment: {segment}")

    # Create an ElementTree object and write it to a file
    tree = ET.ElementTree(root)
    tree.write(originalSUMOline)
    