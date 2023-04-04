from flask import Flask, request

app = Flask(__name__)

@app.route('/gyro_data', methods=['POST'])
def handle_gyro_data():
    if request.method == 'POST':
        gyro_data = request.get_json()
        z_angle = gyro_data.get('z')
        print(z_angle)
        return '', 200
    else:
        return '', 405

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090)