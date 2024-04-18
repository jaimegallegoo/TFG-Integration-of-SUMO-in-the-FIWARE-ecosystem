from flask import Flask, send_from_directory, request, redirect, url_for
import sys
sys.path.append('../scripts/data-conversion/sumo-to-fiware')
from functions_fiware_to_sumo import *
from functions_sumo_to_fiware import *

app = Flask(__name__, static_folder='../web')

# Serve the index.html file
@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

# Serve the SUMO-conversion.html file
@app.route('/SUMO-conversion', methods=['GET', 'POST'])
def conversion():
    if request.method == 'POST':
        convert_SUMO_line()
        return redirect(url_for('city'))
    return send_from_directory(app.static_folder, 'SUMO-conversion.html')

# Serve the city.html file
@app.route('/city')
def city():
    return send_from_directory(app.static_folder, 'city.html')

# Serve any CSS file
@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory(app.static_folder + '/css', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)