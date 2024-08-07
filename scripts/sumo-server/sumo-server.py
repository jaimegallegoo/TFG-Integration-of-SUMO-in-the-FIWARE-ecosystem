import logging
from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/ptlines2flows', methods=['POST'])
def ptlines2flows():
    # Get the input data from the request
    input_data = request.get_json()

    # Define the command as a list to avoid shell injection
    command = [
        'python3', '/usr/share/sumo/tools/ptlines2flows.py', 
        '-n', input_data['osm_net'],
        '-s', input_data['osm_stops'], 
        '-l', input_data['osm_ptlines'], 
        '-i', input_data['stop_infos'],
        '-t', input_data['trips'], 
        '-r', input_data['veh_routes'], 
        '-o', input_data['osm_routes'],
        '-e', '4000',
        '--extend-to-fringe',
        '--random-begin',
        '--seed', '42',
        '--vtype-prefix', 'pt_',
        '--verbose',
        '--ignore-errors',
        '--min-stops', '0'
    ]

    # Run the ptlines2flows.py script with the input data
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check the result and return appropriate response
    if result.returncode == 0:
        return {
            'message': 'ptlines2flows.py script ran successfully',
            'output': result.stdout.decode()
        }, 200
    else:
        return {
            'message': 'Failed to run ptlines2flows.py script',
            'error': result.stderr.decode()
        }, 500
    
@app.route('/test', methods=['GET'])
def test_connection():
    return {'message': 'Connection successful'}, 200

@app.route('/simulation', methods=['POST'])
def emissionsSimulation():
    # Get the input data from the request
    input_data = request.get_json()

    # Run the emissions simulation with the input data
    result = subprocess.run(
        ['sumo', '-c', input_data['osm_sumocfg'], '--emission-output', input_data['emissions'], '--stop-output', input_data['stop'], '--fcd-output', input_data['fcd'], '--use-stop-ended', '--end', input_data['duration']],
        stdout=subprocess.PIPE
    )
    
    # Check the result
    if result.returncode == 0:
        return {'message': 'Emissions simulation ran successfully'}, 200
    else:
        return {'message': 'Failed to run emissions simulation', 'error': result.stdout.decode()}, 500
    
@app.route('/emissionsVisualization', methods=['POST'])
def emissionsVisualization():
    # Get the input data from the request
    input_data = request.get_json()

    # Run the emissions simulation with the input data
    result = subprocess.run(
        ['python3', '/usr/share/sumo/tools/visualization/plotXMLAttributes.py', '-x', 'time', '-y', 'CO2', '-o', input_data['CO2_output'], input_data['emissions'], '-i', 'id'],
        stdout=subprocess.PIPE
    )

    # Check the result
    if result.returncode == 0:
        return {'message': 'plotXMLAttributes.py script ran successfully'}, 200
    else:
        return {'message': 'Failed to run plotXMLAttributes.py script', 'error': result.stdout.decode()}, 500
    
@app.route('/trajectoriesVisualization', methods=['POST'])
def trajectoriesVisualization():
    # Get the input data from the request
    input_data = request.get_json()

    # Run the emissions simulation with the input data
    result = subprocess.run(
        ['python3', '/usr/share/sumo/tools/visualization/plotXMLAttributes.py', '-x', 'x', '-y', 'y', '-o', input_data['trajectories'], input_data['fcd'], '--scatterplot'],
        stdout=subprocess.PIPE
    )

    # Check the result
    if result.returncode == 0:
        return {'message': 'plotXMLAttributes.py script ran successfully'}, 200
    else:
        return {'message': 'Failed to run plotXMLAttributes.py script', 'error': result.stdout.decode()}, 500
    
@app.route('/arrivalVisualization', methods=['POST'])
def arrivalVisualization():
    # Get the input data from the request
    input_data = request.get_json()

    # Run the emissions simulation with the input data
    result = subprocess.run(
        ['python3', '/usr/share/sumo/tools/visualization/plotXMLAttributes.py', '-x', 'depart', '-y', 'arrival', '-o', input_data['arrival'], input_data['vehroutes'], '--scatterplot'],
        stdout=subprocess.PIPE
    )

    # Check the result
    if result.returncode == 0:
        return {'message': 'plotXMLAttributes.py script ran successfully'}, 200
    else:
        return {'message': 'Failed to run plotXMLAttributes.py script', 'error': result.stdout.decode()}, 500
    
@app.route('/personFlow', methods=['POST'])
def personFlow():
    # Get the input data from the request
    input_data = request.get_json()

    # Define the command as a list to avoid shell injection
    command = [
        'python3', '/usr/share/sumo/tools/randomTrips.py', 
        '-n', input_data['osm_net'],
        '-a', input_data['osm_stops'] + ',' + input_data['osm_pt_rou'], 
        '-o', input_data['osm_pedestrian_trips'],
        '-r', input_data['osm_pedestrian_rou'],
        '--persontrips',
        '--persontrip.walk-opposite-factor', '0.8',
        '--prefix', 'ped',
        '--trip-attributes', 'modes="public"',
        '--vehicle-class', 'pedestrian',
        '--fringe-factor', '1',
        '--end', input_data['duration'],
        '--insertion-density', '10'
    ]

    # Run the randomTrips.py script with the input data
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check the result and return appropriate response
    if result.returncode == 0:
        return {
            'message': 'randomTrips.py script ran successfully',
            'output': result.stdout.decode()
        }, 200
    else:
        return {
            'message': 'Failed to run randomTrips.py script',
            'error': result.stderr.decode()
        }, 500
    
@app.route('/personsLoadedVisualization', methods=['POST'])
def personsLoadedVisualization():
    # Get the input data from the request
    input_data = request.get_json()

    # Run the emissions simulation with the input data
    result = subprocess.run(
        ['python3', '/usr/share/sumo/tools/visualization/plotXMLAttributes.py', input_data['stop'], '-i', 'busStop', '-y', 'loadedPersons', '-x', 'lane', '-o', input_data['persons_loaded'], '--scatterplot'],
        stdout=subprocess.PIPE
    )

    # Check the result
    if result.returncode == 0:
        return {'message': 'plotXMLAttributes.py script ran successfully'}, 200
    else:
        return {'message': 'Failed to run plotXMLAttributes.py script', 'error': result.stdout.decode()}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)