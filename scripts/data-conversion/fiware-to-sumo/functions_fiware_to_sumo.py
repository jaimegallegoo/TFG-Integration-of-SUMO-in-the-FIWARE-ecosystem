import os
import requests
import xmltodict
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

import gzip
import shutil

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
        ptLine_attributes = {
            "id": item['routeCode']['value'],
            "name": item['name']['value'],
            "line": item['shortRouteCode']['value'],
            "type": type,
            "vClass": vClass,
        }

        # Only add the "color" attribute if its value is not "No data available"
        if route_color != "No data available":
            ptLine_attributes["color"] = route_color

        # Only add the "period" attribute if its value is not "No data available"
        if period != "No data available":
            ptLine_attributes["period"] = period

        # Only add the "completeness" attribute if its value is not "No data available"
        if completeness != "No data available":
            ptLine_attributes["completeness"] = completeness

        ptLine = ET.SubElement(root, "ptLine", ptLine_attributes)

        # Only add the "edges" attribute if its value is not "No data available"
        if route_edges != "No data available":
            route = ET.SubElement(ptLine, "route", {
            "edges": route_edges
        })        

        # Check if routeSegments value is not "No data available"
        if item['routeSegments']['value'] != "No data available":
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

        if lines != "No data available":
            # Extract the line codes from the URNs
            line_codes = [line.split(':')[-1] for line in lines]

            # Join the line codes into a string
            line_string = ' '.join(line_codes)
        else:
            line_string = lines

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
        busStop_attributes = {
            "id": item['stopCode']['value'],
            "lane": lane,
            "startPos": startPos,
            "endPos": endPos,
            "friendlyPos": friendlyPos,
        }

        # Only add the "name" attribute if its value is not "No data available"
        route_name = item['name']['value']

        if route_name != "No data available":
            busStop_attributes["name"] = route_name

        # Only add the "lines" attribute if its value is not "No data available"
        if line_string != "No data available":
            busStop_attributes["lines"] = line_string

        # Create the busStop element
        busStop = ET.SubElement(root, "busStop", busStop_attributes)

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

    # Delete the original osm.sumocfg file from the modified folder
    #os.system(f'rm {modifiedSUMOfolder}/osm.sumocfg')

    # Copy the corrected osm.sumocfg file to the modified folder
    #os.system(f'cp ../../../data/input/sumo/simulation_config/osm.sumocfg {modifiedSUMOfolder}')

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

    # ONLY FOR OLD VERSIONS OF SUMO
    # ---------------------------------------------------------------------

    # Extract "osm.net.xml" from "osm.net.xml.gz"
    #with gzip.open(f'{modifiedSUMOfolder}/osm.net.xml.gz', 'rb') as f_in:
    #    with open(f'{modifiedSUMOfolder}/osm.net.xml', 'wb') as f_out:
    #        shutil.copyfileobj(f_in, f_out)

    # Extract "osm.poly.xml" from "osm.poly.xml.gz"
    #with gzip.open(f'{modifiedSUMOfolder}/osm.poly.xml.gz', 'rb') as f_in:
    #    with open(f'{modifiedSUMOfolder}/osm.poly.xml', 'wb') as f_out:
    #        shutil.copyfileobj(f_in, f_out)

    # ---------------------------------------------------------------------

    # Generate the routes file based on the lines and stops
    sumo_home = os.getenv('SUMO_HOME') # C:\Program Files (x86)\Eclipse\Sumo
    osm_net = f'../../../data/output/sumo/{city}/osm.net.xml.gz'
    stop_infos = f'../../../data/output/sumo/{city}/stopinfos.xml'
    trips = f'../../../data/output/sumo/{city}/trips.trips.xml'
    veh_routes = f'../../../data/output/sumo/{city}/vehroutes.xml'
    osm_routes = f'../../../data/output/sumo/{city}/osm_pt.rou.xml'
    os.system(f'python ../../../data/ptlines2flows.py -n {osm_net} -s {osm_stops} -l {osm_ptlines} -i {stop_infos} -t {trips} -r {veh_routes} -o {osm_routes} -e 4000 --extend-to-fringe --random-begin --seed 42 --vtype-prefix pt_ --verbose --ignore-errors --min-stops 0')
    
    # Delete the temporal JSON files
    os.remove(modifiedFIWAREroute) 
    os.remove(modifiedFIWAREstop)

# ---------------------------------------------------------------------

# This function converts the lines and stops from the selected city in the application to SUMO. DESIGNED FOR THE WEB INTERFACE
def convert_FIWARE_city_web(city):
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

    # Delete the original osm.sumocfg file from the modified folder
    #os.system(f'rm {modifiedSUMOfolder}/osm.sumocfg')

    # Copy the corrected osm.sumocfg file to the modified folder
    #os.system(f'cp ../../../data/input/sumo/simulation_config/osm.sumocfg {modifiedSUMOfolder}')

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

    # ONLY FOR OLD VERSIONS OF SUMO
    # ---------------------------------------------------------------------

    # Extract "osm.net.xml" from "osm.net.xml.gz"
    #with gzip.open(f'{modifiedSUMOfolder}/osm.net.xml.gz', 'rb') as f_in:
    #    with open(f'{modifiedSUMOfolder}/osm.net.xml', 'wb') as f_out:
    #        shutil.copyfileobj(f_in, f_out)

    # Extract "osm.poly.xml" from "osm.poly.xml.gz"
    #with gzip.open(f'{modifiedSUMOfolder}/osm.poly.xml.gz', 'rb') as f_in:
    #    with open(f'{modifiedSUMOfolder}/osm.poly.xml', 'wb') as f_out:
    #        shutil.copyfileobj(f_in, f_out)

    # ---------------------------------------------------------------------

    # Generate the routes file based on the lines and stops
    sumo_home = os.getenv('SUMO_HOME') # C:\Program Files (x86)\Eclipse\Sumo
    osm_net = f'../../../data/output/sumo/{city}/osm.net.xml.gz'
    stop_infos = f'../../../data/output/sumo/{city}/stopinfos.xml'
    trips = f'../../../data/output/sumo/{city}/trips.trips.xml'
    veh_routes = f'../../../data/output/sumo/{city}/vehroutes.xml'
    osm_routes = f'../../../data/output/sumo/{city}/osm_pt.rou.xml'

    # CHANGES FOR THE WEB INTERFACE
    # Define the URL of the Flask app in the sumo-server container
    url = 'http://sumo-server:5000/ptlines2flows'

    # Define the data to send to the Flask app
    data = {
        'osm_net': osm_net,
        'osm_stops': osm_stops,
        'osm_ptlines': osm_ptlines,
        'stop_infos': stop_infos,
        'trips': trips,
        'veh_routes': veh_routes,
        'osm_routes': osm_routes,
    }

    # Make a POST request to the Flask app
    response = requests.post(url, json=data)

    # Check the response
    if response.status_code == 200:
        print('ptlines2flows.py script ran successfully')
        # Check if the output file exists
        if os.path.exists(osm_routes):
            print('Output file was successfully created')
        else:
            print('Failed to create output file')
    else:
        print('Failed to run ptlines2flows.py script:', response.text)
    
    # Delete the temporal JSON files
    os.remove(modifiedFIWAREroute) 
    os.remove(modifiedFIWAREstop)

# ---------------------------------------------------------------------

def test_sumo_server():
    url = 'http://localhost:5000/test'  # Use localhost instead of sumo-server
    response = requests.get(url)

    if response.status_code == 200:
        print('Connection to sumo-server is successful')
    else:
        print('Failed to connect to sumo-server')

# ---------------------------------------------------------------------

def test_sumo_server_web():
    url = 'http://sumo-server:5000/test'
    response = requests.get(url)

    if response.status_code == 200:
        print('Connection to sumo-server is successful')
    else:
        print('Failed to connect to sumo-server')

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

# ---------------------------------------------------------------------

# This function generates the simulation for the selected scenario
def generate_simulation(city, duration):
    # Set the folder for the SUMO output files
    modifiedSUMOfolder = f'../../../data/output/sumo/{city}'

    # Define the path for the SUMO configuration file
    osm_sumocfg = f'../../../data/output/sumo/{city}/osm.sumocfg'

    # Define the path for the emissions output file
    emissions = f'../../../data/output/sumo/{city}/emissions.xml'

    # Define the path for the stop output file
    stop = f'../../../data/output/sumo/{city}/stop.xml'

    # Define the path for the fcd output file
    fcd = f'../../../data/output/sumo/{city}/fcd.xml'

    # Run the SUMO simulation with the emissions output
    os.system(f'sumo -c {osm_sumocfg} --emission-output {emissions} --stop-output {stop} --fcd-output {fcd} --use-stop-ended --end {duration}')
    # sumo -c osm.sumocfg --emission-output emissions.xml --use-stop-ended --end 3600
    # sumo -c osm.sumocfg --emission-output emissions.xml --stop-output stop.xml --fcd-output fcd.xml --use-stop-ended --end 4000

# ---------------------------------------------------------------------

# This function generates the emissions for the selected simulation. DESIGNED FOR THE WEB INTERFACE
def generate_simulation_web(city, duration):
    # Set the folder for the SUMO output files
    modifiedSUMOfolder = f'../../../data/output/sumo/{city}'

    # Define the path for the SUMO configuration file
    osm_sumocfg = f'../../../data/output/sumo/{city}/osm.sumocfg'

    # Define the path for the emissions output file
    emissions = f'../../../data/output/sumo/{city}/emissions.xml'

    # Define the path for the stop output file
    stop = f'../../../data/output/sumo/{city}/stop.xml'

    # Define the path for the fcd output file
    fcd = f'../../../data/output/sumo/{city}/fcd.xml'

    # Run the SUMO simulation with the emissions output

    # CHANGES FOR THE WEB INTERFACE
    # Define the URL of the Flask app in the sumo-server container
    url = 'http://sumo-server:5000/simulation'

    # Define the data to send to the Flask app
    data = {
        'osm_sumocfg': osm_sumocfg,
        'emissions': emissions,
        'duration': duration,
        'stop': stop,
        'fcd': fcd
    }

    # Make a POST request to the Flask app
    response = requests.post(url, json=data)

    # Check the response
    if response.status_code == 200:
        print('Emissions simulation ran successfully')
        # Check if the output file exists
        if os.path.exists(emissions):
            print('Output file was successfully created')
        else:
            print('Failed to create output file')
    else:
        print('Failed to run the emissions simulation:', response.text)

# ---------------------------------------------------------------------

# This function generates the emissions visualization for the selected simulation
def generate_emissions_visualization(city):
    # Set the folder for the SUMO output files
    modifiedSUMOfolder = f'../../../data/output/sumo/{city}'

    # Define the path for the emissions input file
    emissions = f'../../../data/output/sumo/{city}/emissions.xml'

    # Define the path for the emissions image output file
    CO2_output = f'../../../data/output/sumo/{city}/CO2_output.png'

    # Run the SUMO visualization tool to plot the emissions
    sumo_home = os.getenv('SUMO_HOME') # C:\Program Files (x86)\Eclipse\Sumo
    os.system(f'python "{sumo_home}/tools/visualization/plotXMLAttributes.py" -x time -y CO2 -o {CO2_output} {emissions} -i id')
    # python $SUMO_HOME/tools/visualization/plotXMLAttributes.py -x time -y CO2 -o CO2_output.png emissions.xml -i id

# ---------------------------------------------------------------------    

# This function generates the emissions visualization for the selected simulation. DESIGNED FOR THE WEB INTERFACE
def generate_emissions_visualization_web(city):
    # Set the folder for the SUMO output files
    modifiedSUMOfolder = f'../../../data/output/sumo/{city}'

    # Define the path for the emissions input file
    emissions = f'../../../data/output/sumo/{city}/emissions.xml'

    # Define the path for the emissions image output file
    CO2_output = f'../../../data/output/sumo/{city}/CO2_output.png'

    # Run the SUMO visualization tool to plot the emissions

    # CHANGES FOR THE WEB INTERFACE
    # Define the URL of the Flask app in the sumo-server container
    url = 'http://sumo-server:5000/emissionsVisualization'

    # Define the data to send to the Flask app
    data = {
        'emissions': emissions,
        'CO2_output': CO2_output
    }

    # Make a POST request to the Flask app
    response = requests.post(url, json=data)

    # Check the response
    if response.status_code == 200:
        print('plotXMLAttributes.py script ran successfully')
        # Check if the output file exists
        if os.path.exists(CO2_output):
            print('Output file was successfully created')
        else:
            print('Failed to create output file')
    else:
        print('Failed to run plotXMLAttributes.py script:', response.text)

# ---------------------------------------------------------------------   

# This function generates the trajectories visualization for the selected simulation. DESIGNED FOR THE WEB INTERFACE
def generate_trajectories_visualization_web(city):
    # Set the folder for the SUMO output files
    modifiedSUMOfolder = f'../../../data/output/sumo/{city}'

    # Define the path for the fcd input file
    fcd = f'../../../data/output/sumo/{city}/fcd.xml'

    # Define the path for the trajectories image output file
    trajectories = f'../../../data/output/sumo/{city}/trajectories.png'

    # Run the SUMO visualization tool to plot the trajectories

    # CHANGES FOR THE WEB INTERFACE
    # Define the URL of the Flask app in the sumo-server container
    url = 'http://sumo-server:5000/trajectoriesVisualization'

    # Define the data to send to the Flask app
    data = {
        'fcd': fcd,
        'trajectories': trajectories
    }

    # Make a POST request to the Flask app
    response = requests.post(url, json=data)

    # Check the response
    if response.status_code == 200:
        print('plotXMLAttributes.py script ran successfully')
        # Check if the output file exists
        if os.path.exists(trajectories):
            print('Output file was successfully created')
        else:
            print('Failed to create output file')
    else:
        print('Failed to run plotXMLAttributes.py script:', response.text)

# ---------------------------------------------------------------------   

# This function generates the arrival visualization for the selected simulation. DESIGNED FOR THE WEB INTERFACE
def generate_arrival_visualization_web(city):
    # Set the folder for the SUMO output files
    modifiedSUMOfolder = f'../../../data/output/sumo/{city}'

    # Define the path for the vehroutes input file
    vehroutes = f'../../../data/output/sumo/{city}/vehroutes.xml'

    # Define the path for the arrival image output file
    arrival = f'../../../data/output/sumo/{city}/arrival.png'

    # Run the SUMO visualization tool to plot the trajectories

    # CHANGES FOR THE WEB INTERFACE
    # Define the URL of the Flask app in the sumo-server container
    url = 'http://sumo-server:5000/arrivalVisualization'

    # Define the data to send to the Flask app
    data = {
        'vehroutes': vehroutes,
        'arrival': arrival
    }

    # Make a POST request to the Flask app
    response = requests.post(url, json=data)

    # Check the response
    if response.status_code == 200:
        print('plotXMLAttributes.py script ran successfully')
        # Check if the output file exists
        if os.path.exists(arrival):
            print('Output file was successfully created')
        else:
            print('Failed to create output file')
    else:
        print('Failed to run plotXMLAttributes.py script:', response.text)

# --------------------------------------------------------------------- 

# This function generates a person flow for the selected simulation. DESIGNED FOR THE WEB INTERFACE
def generate_person_flow_web(city, duration):
    # Set the folder for the SUMO output files
    modifiedSUMOfolder = f'../../../data/output/sumo/{city}'

    # Define the path for the network input file
    osm_net = f'../../../data/output/sumo/{city}/osm.net.xml.gz'

    # Define the path for the stops input file
    osm_stops = f'../../../data/output/sumo/{city}/osm_stops.add.xml'

    # Define the path for the public transport routes input file
    osm_pt_rou = f'../../../data/output/sumo/{city}/osm_pt.rou.xml'

    # Define the path for the person trips output file
    osm_pedestrian_trips = f'../../../data/output/sumo/{city}/osm.pedestrian.trips.xml'

    # Define the path for the person routes output file
    osm_pedestrian_rou = f'../../../data/output/sumo/{city}/osm.pedestrian.rou.xml'

    # Run the SUMO simulation with the emissions output

    # CHANGES FOR THE WEB INTERFACE
    # Define the URL of the Flask app in the sumo-server container
    url = 'http://sumo-server:5000/personFlow'

    # Define the data to send to the Flask app
    data = {
        'osm_net': osm_net,
        'osm_stops': osm_stops,
        'osm_pt_rou': osm_pt_rou,
        'osm_pedestrian_trips': osm_pedestrian_trips,
        'osm_pedestrian_rou': osm_pedestrian_rou,
        'duration': duration
    }

    # Make a POST request to the Flask app
    response = requests.post(url, json=data)

    # Check the response
    if response.status_code == 200:
        print('Emissions simulation ran successfully')
        # Check if the output file exists
        if os.path.exists(osm_pedestrian_rou):
            print('Output file was successfully created')
        else:
            print('Failed to create output file')
    else:
        print('Failed to run the emissions simulation:', response.text)

# ---------------------------------------------------------------------

# This function generates the persons loaded visualization for the selected simulation. DESIGNED FOR THE WEB INTERFACE
def generate_persons_loaded_visualization_web(city):
    # Set the folder for the SUMO output files
    modifiedSUMOfolder = f'../../../data/output/sumo/{city}'

    # Define the path for the stop input file
    stop = f'../../../data/output/sumo/{city}/stop.xml'

    # Define the path for the persons loaded image output file
    persons_loaded = f'../../../data/output/sumo/{city}/persons_loaded.png'

    # Run the SUMO visualization tool to plot the trajectories

    # CHANGES FOR THE WEB INTERFACE
    # Define the URL of the Flask app in the sumo-server container
    url = 'http://sumo-server:5000/personsLoadedVisualization'

    # Define the data to send to the Flask app
    data = {
        'stop': stop,
        'persons_loaded': persons_loaded
    }

    # Make a POST request to the Flask app
    response = requests.post(url, json=data)

    # Check the response
    if response.status_code == 200:
        print('plotXMLAttributes.py script ran successfully')
        # Check if the output file exists
        if os.path.exists(persons_loaded):
            print('Output file was successfully created')
        else:
            print('Failed to create output file')
    else:
        print('Failed to run plotXMLAttributes.py script:', response.text)

# --------------------------------------------------------------------- 

# This function launches a simulation for the selected city and creates the emissions visualization
def simulate_new_scenario(city, duration, personFlow):
    # Generate the simulation
    generate_simulation_web(city, duration)

    # If personFlow is True, generate the person flow visualization
    if personFlow:
        generate_person_flow_web(city, duration)
        generate_persons_loaded_visualization_web(city)
        
        # Copy the "persons_loaded.png" file to the web-server "static" folder
        os.system(f'cp ../../../data/output/sumo/{city}/persons_loaded.png ../../../web/images/simulation/persons_loaded_{city}.png')
    
    # Generate the emissions visualization
    generate_emissions_visualization_web(city)

    # Generate the trajectories visualization
    generate_trajectories_visualization_web(city)

    # Generate the arrival visualization
    generate_arrival_visualization_web(city)

    # Copy the "CO2_output.png" file to the web-server "static" folder
    os.system(f'cp ../../../data/output/sumo/{city}/CO2_output.png ../../../web/images/simulation/CO2_output_{city}.png')

    # Copy the "trajectories.png" file to the web-server "static" folder
    os.system(f'cp ../../../data/output/sumo/{city}/trajectories.png ../../../web/images/simulation/trajectories_{city}.png')

    # Copy the "arrival.png" file to the web-server "static" folder
    os.system(f'cp ../../../data/output/sumo/{city}/arrival.png ../../../web/images/simulation/arrival_{city}.png')

    return {'message': 'Simulation ran successfully'}