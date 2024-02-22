import os
from flask import Flask, request
from flask import jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/processManualUpload', methods=['POST'])
def processManualUpload():
	print('Received request for /processManualUpload')
	# Rest of your code...
	# print recived data
	print(request.json)
	return jsonify(message="Success")

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
