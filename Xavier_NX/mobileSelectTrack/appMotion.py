from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/motion-data', methods=['POST'])
def motion_data():
    data = json.loads(request.data)
    # Do something with the motion data (e.g., store it in a database)
    return 'Motion data received'

if __name__ == '__main__':
    app.run(host='192.168.31.177', port=9090)
