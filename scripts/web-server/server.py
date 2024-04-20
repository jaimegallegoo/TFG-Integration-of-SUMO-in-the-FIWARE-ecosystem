from flask import Flask, send_from_directory, request, redirect, url_for, jsonify
from flask import render_template
import sys
sys.path.append('/data-conversion/sumo-to-fiware')
sys.path.append('/data-conversion/fiware-to-sumo')
from functions_fiware_to_sumo import *
from functions_sumo_to_fiware import *

app = Flask(__name__, static_folder='../web', template_folder='../web/templates')

# Serve the index.html file
@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

# Serve any CSS file
@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory(app.static_folder + '/css', path)

# Serve the SUMO-conversion.html file
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

    return send_from_directory(app.static_folder, 'SUMO-conversion.html')

# Serve the city.html file
@app.route('/cities/<city>')
def city(city):
    # Fetch data from the Orion Context Broker
    routes_response = requests.get('http://orion:1026/v2/entities?type=PublicTransportRoute&options=keyValues')
    stops_response = requests.get('http://orion:1026/v2/entities?type=PublicTransportStop&options=keyValues')

    # Convert the response to JSON
    routes = routes_response.json()
    stops = stops_response.json()

    # Pass the data to the template
    return render_template('city.html', city=city, routes=routes, stops=stops)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)