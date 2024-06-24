from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/ptlines2flows', methods=['POST'])
def ptlines2flows():
    # Get the input data from the request
    input_data = request.get_json()

    # Run the ptlines2flows.py script with the input data
    result = subprocess.run(
        ['python3', '/usr/share/sumo/tools/ptlines2flows.py', '-n', input_data['osm_net'],
        '-s', input_data['osm_stops'], '-l', input_data['osm_ptlines'], '-i', input_data['stop_infos'],
        '-t', input_data['trips'], '-r', input_data['veh_routes'], '-o', input_data['osm_routes'],
        '--ignore-errors', '--min-stops', '0', '-e', '4000', '--extend-to-fringe', '--random-begin',
        '--seed', '42', '--vtype-prefix', 'pt_', '--verbose'], stdout=subprocess.PIPE)

    # Check the result
    if result.returncode == 0:
        return {'message': 'ptlines2flows.py script ran successfully'}, 200
    else:
        return {'message': 'Failed to run ptlines2flows.py script', 'error': result.stdout.decode()}, 500
    
@app.route('/test', methods=['GET'])
def test_connection():
    return {'message': 'Connection successful'}, 200

@app.route('/emissionsSimulation', methods=['POST'])
def emissionsSimulation():
    # Get the input data from the request
    input_data = request.get_json()

    # Run the emissions simulation with the input data
    result = subprocess.run(
        ['sumo', '-c', input_data['osm_sumocfg'], '--emission-output', input_data['emissions'], '--use-stop-ended', '--end', input_data['duration']],
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)