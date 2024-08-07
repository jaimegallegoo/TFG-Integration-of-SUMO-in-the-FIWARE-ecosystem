from flask import Flask, send_from_directory, request, redirect, url_for, jsonify, make_response
from flask import render_template
import sys, os
sys.path.append('/data-conversion/sumo-to-fiware')
sys.path.append('/data-conversion/fiware-to-sumo')
from functions_fiware_to_sumo import *
from functions_sumo_to_fiware import *

app = Flask(__name__, static_folder='../web', template_folder='../web/templates')

# Serve the index.html file
@app.route('/')
def home():
    return render_template('index.html')

# Serve any CSS file
@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory(app.static_folder + '/css', path)

# Serve the SUMO-conversion.html file and handle the conversion
@app.route('/SUMO-conversion', methods=['GET', 'POST'])
def conversion():
    if request.method == 'POST':
        # Get the city from the POST request data
        data = request.get_json()
        city = data.get('city')

        # Call the function to convert the data
        result = convert_SUMO_city(city)

        # Return the result as a JSON response
        return jsonify(result)

    return render_template('SUMO-conversion.html')

# Serve the city.html file
@app.route('/cities/<city>')
def city(city):
    # Fetch data from the Orion Context Broker
    routes_response = requests.get(f'http://orion:1026/v2/entities/?type=PublicTransportRoute&options=keyValues&q=address.addressLocality=={city.capitalize()}&limit=1000')
    stops_response = requests.get(f'http://orion:1026/v2/entities/?type=PublicTransportStop&options=keyValues&q=address.addressLocality=={city.capitalize()}&limit=1000')

    # Convert the response to JSON
    routes = routes_response.json()
    stops = stops_response.json()

    # Pass the data to the template
    return render_template('city.html', city=city, routes=routes, stops=stops)

# Serve the routes.html file
@app.route('/cities/<city>/routes')
def routes(city):
    # Fetch data from the Orion Context Broker
    routes_response = requests.get(f'http://orion:1026/v2/entities/?type=PublicTransportRoute&options=keyValues&q=address.addressLocality=={city.capitalize()}&limit=1000')

    # Fetch the bus routes
    bus_routes_response = requests.get(f'http://orion:1026/v2/entities/?type=PublicTransportRoute&options=keyValues&q=address.addressLocality=={city.capitalize()};transportationType==3&limit=1000')

    # Fetch the train routes
    train_routes_response = requests.get(f'http://orion:1026/v2/entities/?type=PublicTransportRoute&options=keyValues&q=address.addressLocality=={city.capitalize()};transportationType==2&limit=1000')

    # Fetch the subway routes
    subway_routes_response = requests.get(f'http://orion:1026/v2/entities/?type=PublicTransportRoute&options=keyValues&q=address.addressLocality=={city.capitalize()};transportationType==1&limit=1000')

    # Convert the responses to JSON
    routes = routes_response.json()
    bus_routes = bus_routes_response.json()
    train_routes = train_routes_response.json()
    subway_routes = subway_routes_response.json()

    # Pass the data to the template
    return render_template('routes.html', city=city, routes=routes, bus_routes=bus_routes, train_routes=train_routes, subway_routes=subway_routes)

# Serve the stops.html file
@app.route('/cities/<city>/stops')
def stops(city):
    # Fetch data from the Orion Context Broker
    stops_response = requests.get(f'http://orion:1026/v2/entities/?type=PublicTransportStop&options=keyValues&q=address.addressLocality=={city.capitalize()}&limit=1000')

    # Convert the response to JSON
    stops = stops_response.json()

    # Pass the data to the template
    return render_template('stops.html', city=city, stops=stops)

# Serve the routeDetails.html file
@app.route('/cities/<city>/routes/<shortRouteCode>/<routeCode>', methods=['GET', 'DELETE'])
def routeDetails(city, routeCode, shortRouteCode):
    if request.method == 'GET':
        # Fetch data from the Orion Context Broker
        route_response = requests.get(f'http://orion:1026/v2/entities/urn:ngsi-ld:PublicTransportRoute:{city}:transport:busLine:{shortRouteCode}?q=routeCode=={routeCode}')

        # Convert the responses to JSON
        route = route_response.json()

        # Pass the data to the template
        return render_template('routeDetails.html', city=city, route=route)
    
    elif request.method == 'DELETE':
        # Perform the deletion operation here
        # For example, you might send a DELETE request to the Orion Context Broker
        delete_response = requests.delete(f'http://orion:1026/v2/entities/urn:ngsi-ld:PublicTransportRoute:{city}:transport:busLine:{shortRouteCode}')

        # Return a response to indicate that the deletion was successful
        return jsonify({'message': 'Route deleted successfully'}), 200
    
# Serve the stopDetails.html file
@app.route('/cities/<city>/stops/<stopCode>', methods=['GET', 'DELETE'])
def stopDetails(city, stopCode):
    if request.method == 'GET':
        # Fetch data from the Orion Context Broker
        stop_response = requests.get(f'http://orion:1026/v2/entities/urn:ngsi-ld:PublicTransportStop:{city}:busStop:{stopCode}')

        # Convert the responses to JSON
        stop = stop_response.json()

        # Pass the data to the template
        return render_template('stopDetails.html', city=city, stop=stop)
    
    elif request.method == 'DELETE':
        # Perform the deletion operation here
        # For example, you might send a DELETE request to the Orion Context Broker
        delete_response = requests.delete(f'http://orion:1026/v2/entities/urn:ngsi-ld:PublicTransportStop:{city}:busStop:{stopCode}')

        # Return a response to indicate that the deletion was successful
        return jsonify({'message': 'Stop deleted successfully'}), 200
    
# Serve the SUMO-conversion.html file
@app.route('/FIWARE-conversion', methods=['GET', 'POST'])
def conversionToSUMO():
    if request.method == 'POST':
        # Get the city from the POST request data
        data = request.get_json()
        city = data.get('city')

        # Call the function to convert the data
        result = convert_FIWARE_city_web(city)

        # Return the result as a JSON response
        return jsonify(result)

    return send_from_directory(app.static_folder, 'FIWARE-conversion.html')

# Serve the simulation.html file and handle the simulation
@app.route('/cities/<city>/simulation', methods=['GET', 'POST'])
def simulation(city):
    if request.method == 'POST':
        # Get the city and the duration from the POST request data
        data = request.get_json()
        city = data.get('city')
        duration = data.get('duration')
        personFlow = data.get('personFlow')

        if not city or not duration:
            return make_response(jsonify({"error": "Missing city or duration"}), 400)

        try:
            # Call the function to convert the data
            result = simulate_new_scenario(city, duration, personFlow)
        except Exception as e:
            return make_response(jsonify({"error": str(e)}), 500)

        # Return the result as a JSON response
        return jsonify(result)
    
    elif request.method == 'GET':
        return render_template('simulation.html', city=city)
    
# Serve the stats.html file
@app.route('/cities/<city>/stats', methods=['GET'])
def stats(city):
    # Construct the path for the image file
    image_path = os.path.join(app.static_folder, 'images', f'persons_loaded_{city}.png')
    # Check if the image file exists
    persons_loaded = os.path.exists(image_path)
    # Render the template with the additional variable
    return render_template('stats.html', city=city, persons_loaded=persons_loaded)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)