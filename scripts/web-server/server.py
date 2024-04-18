from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='../web')

# Serve the index.html file
@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

# Serve the SUMO-conversion.html file
@app.route('/SUMO-conversion')
def about():
    return send_from_directory(app.static_folder, 'SUMO-conversion.html')

# Serve any CSS file
@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory(app.static_folder + '/css', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)